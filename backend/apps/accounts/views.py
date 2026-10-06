"""Accounts views: authentication, profiles, user management, and programs."""
import csv
import logging
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UserProfile, Program
from .profile_list_filters import apply_profile_list_filters
from apps.common.http.permissions import IsStaffOrSuperUser, IsSuperUser
from apps.common.http.pagination import StandardResultsSetPagination
from .csv_services import process_program_csv
from .services.roster_sync import StudentRosterParser, classify_roster_diff, execute_roster_sync
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserProfileListSerializer,
    DepartmentSerializer,
    CourseSerializer,
    ProgramSerializer,
)
from apps.common.models import ActivityLog
from apps.common.core.utils import get_client_ip

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token login view returning extended user info."""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """Public registration for students."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if not getattr(settings, 'ALLOW_PUBLIC_REGISTRATION', False):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Public registration is currently disabled. Please contact your administrator.")
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        ActivityLog.objects.create(
            user=user,
            action=ActivityLog.ActionType.REGISTER,
            resource_type='user',
            resource_id=str(user.id),
            description=f"User {user.username} registered an account.",
            ip_address=get_client_ip(request),
        )

        return Response({
            'message': 'Registration successful. You may now log in.',
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Current authenticated user and profile."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        UserProfile.objects.get_or_create(user=self.request.user)
        return self.request.user


class UserProfileViewSet(viewsets.ModelViewSet):
    """Manage student user profiles."""
    queryset = UserProfile.objects.select_related('user', 'department', 'course').all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=['get', 'patch', 'put'])
    def me(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        if not new_password or len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        profile = user.profile
        if getattr(profile, 'must_change_password', False):
            profile.must_change_password = False
            profile.save(update_fields=['must_change_password'])
            
        return Response({'message': 'Password successfully changed.'})


class DepartmentListView(generics.ListAPIView):
    """Public list of departments."""
    permission_classes = [AllowAny]
    serializer_class = DepartmentSerializer
    queryset = Program.objects.filter(program_type=Program.ProgramType.DEPARTMENT, is_active=True)


class CourseListView(generics.ListAPIView):
    """Public list of courses, filterable by department."""
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer

    def get_queryset(self):
        qs = Program.objects.filter(program_type=Program.ProgramType.COURSE, is_active=True)
        dept = self.request.query_params.get('department')
        if dept:
            qs = qs.filter(department__code=dept)
        return qs


class ProgramViewSet(viewsets.ModelViewSet):
    """Admin CRUD for academic programs (departments & courses)."""
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsStaffOrSuperUser]

    @action(detail=False, methods=['post'], url_path='import-csv')
    def import_csv(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded = request.FILES['file']
        if not uploaded.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV file'}, status=status.HTTP_400_BAD_REQUEST)

        preview_only = str(request.query_params.get('preview_only', 'false')).lower() == 'true'

        success, response_data, status_code = process_program_csv(uploaded, preview_only)
        
        return Response(response_data, status=status_code)

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        try:
            program_type_filter = request.query_params.get('program_type')
            queryset = self.get_queryset().select_related('department')
            if program_type_filter:
                queryset = queryset.filter(program_type=program_type_filter)

            from django.http import StreamingHttpResponse

            class Echo:
                def write(self, value):
                    return value

            def csv_generator():
                pseudo_buffer = Echo()
                writer = csv.writer(pseudo_buffer)
                yield pseudo_buffer.write('\ufeff')
                yield writer.writerow(['name', 'code', 'program_type', 'department_code'])
                for program in queryset.iterator(chunk_size=1000):
                    dept_code = program.department.code if program.department else ''
                    yield writer.writerow([program.name, program.code, program.program_type, dept_code])

            response = StreamingHttpResponse(csv_generator(), content_type='text/csv; charset=utf-8')
            filename = f"programs_export{('_' + program_type_filter) if program_type_filter else ''}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response
        except Exception as exc:
            logger.error('Error exporting program CSV: %s', exc, exc_info=True)
            return Response({'error': 'Error exporting CSV.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserManagementViewSet(viewsets.ModelViewSet):
    """Admin user and profile management."""
    queryset = UserProfile.objects.select_related('user', 'department', 'course').all()
    permission_classes = [IsStaffOrSuperUser]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return UserProfileListSerializer
        return UserProfileSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return apply_profile_list_filters(queryset, self.request.query_params, include_email_search=True)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser])
    def toggle_active(self, request, pk=None):
        profile = self.get_object()
        profile.user.is_active = not profile.user.is_active
        profile.user.save()
        return Response({'is_active': profile.user.is_active, 'message': f"User active status changed to {profile.user.is_active}"})

    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser])
    def toggle_staff(self, request, pk=None):
        profile = self.get_object()
        profile.user.is_staff = not profile.user.is_staff
        profile.user.save()
        return Response({'is_staff': profile.user.is_staff, 'message': f"User staff status changed to {profile.user.is_staff}"})

    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser])
    def reset_password(self, request, pk=None):
        profile = self.get_object()
        new_password = request.data.get('new_password', '').strip()
        if not new_password or len(new_password) < 8:
            return Response({'error': 'New password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)
        profile.user.set_password(new_password)
        profile.user.save()
        return Response({'message': 'Password reset successfully'})

    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser])
    def set_role(self, request, pk=None):
        profile = self.get_object()
        role = request.data.get('role', '').lower()
        if role == 'admin':
            profile.user.is_superuser = True
            profile.user.is_staff = True
        elif role == 'staff':
            profile.user.is_superuser = False
            profile.user.is_staff = True
        elif role == 'student':
            profile.user.is_superuser = False
            profile.user.is_staff = False
        else:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        profile.user.save()
        return Response({'message': f"Role updated to {role}"})

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()


@api_view(['GET'])
@permission_classes([IsStaffOrSuperUser])
def user_count_view(request):
    """Aggregate user counts for admin dashboard."""
    total_users = User.objects.count()
    total_students = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_staff = User.objects.filter(is_staff=True, is_superuser=False).count()
    total_admins = User.objects.filter(is_superuser=True).count()
    return Response({
        'total_users': total_users,
        'total_students': total_students,
        'total_staff': total_staff,
        'total_admins': total_admins,
    })

# --- Student Roster Synchronization --------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrSuperUser])
def student_roster_preview(request):
    """
    Dry-run endpoint for student roster synchronization.
    Parses uploaded .xlsx or .csv, validates formatting, and calculates diffs
    without mutating the database.
    """
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response(
            {'error': 'A valid spreadsheet file (.xlsx or .csv) is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    parser = StudentRosterParser()
    valid_rows, error_rows = parser.parse_file(uploaded_file, uploaded_file.name)

    if not valid_rows and error_rows and error_rows[0].get('field') in ('format', 'dependency', 'file', 'header'):
        return Response(
            {
                'error': error_rows[0]['error'],
                'errors': error_rows,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    diff = classify_roster_diff(valid_rows)

    return Response(
        {
            'filename': uploaded_file.name,
            'stats': {
                'total_rows': len(valid_rows) + len(error_rows),
                'valid_count': len(valid_rows),
                'error_count': len(error_rows),
                'to_create_count': diff['stats']['to_create_count'],
                'to_update_count': diff['stats']['to_update_count'],
                'to_deactivate_count': diff['stats']['to_deactivate_count'],
            },
            'errors': error_rows,
            'preview': {
                'to_create': diff['to_create'][:100],
                'to_update': diff['to_update'][:100],
                'to_deactivate': diff['to_deactivate'][:100],
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrSuperUser])
def student_roster_import(request):
    """
    Atomic execution endpoint for student roster synchronization.
    Parses uploaded file, executes creates/updates within a single database transaction,
    flags must_change_password=True for new accounts, logs ActivityLog, and clears cache.
    """
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response(
            {'error': 'A valid spreadsheet file (.xlsx or .csv) is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    deactivate_unlisted_raw = request.data.get('deactivate_unlisted', 'false')
    deactivate_unlisted = str(deactivate_unlisted_raw).lower() in ('true', '1', 'yes')

    parser = StudentRosterParser()
    valid_rows, error_rows = parser.parse_file(uploaded_file, uploaded_file.name)

    if not valid_rows:
        return Response(
            {
                'error': 'No valid student records were found in the uploaded file.',
                'errors': error_rows,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    diff = classify_roster_diff(valid_rows)

    result = execute_roster_sync(
        diff=diff,
        deactivate_unlisted=deactivate_unlisted,
        actor_user=request.user,
        ip_address=get_client_ip(request),
    )

    return Response(
        {
            'message': 'Student roster synchronized successfully.',
            'created_count': result['created_count'],
            'updated_count': result['updated_count'],
            'deactivated_count': result['deactivated_count'],
            'total_synced': result['total_synced'],
            'errors_count': len(error_rows),
            'errors': error_rows,
        },
        status=status.HTTP_200_OK,
    )
