"""Accounts views: authentication, profiles, user management, and programs."""
import csv
import io
import logging
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
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

            response = HttpResponse(content_type='text/csv; charset=utf-8')
            filename = f"programs_export{('_' + program_type_filter) if program_type_filter else ''}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write('\ufeff')

            writer = csv.writer(response)
            writer.writerow(['name', 'code', 'program_type', 'department_code'])

            for program in queryset:
                dept_code = program.department.code if program.department else ''
                writer.writerow([program.name, program.code, program.program_type, dept_code])

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
