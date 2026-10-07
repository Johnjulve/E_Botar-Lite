"""Common views: health check, system logs, version, branding, academic year."""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
from rest_framework.views import APIView

from .models import SecurityEvent, ActivityLog, SystemSettings
from .http.permissions import IsStaffOrSuperUser, IsSuperUser
from .http.pagination import StandardResultsSetPagination
from .serializers import ActivityLogSerializer, SecurityEventSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([])
def health_check(request):
    """Health check endpoint with active probes and unthrottled access."""
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception as e:
        logger.error(f"Health check DB probe failed: {e}")

    cache_ok = False
    try:
        cache.set('health_probe', 'ok', timeout=5)
        if cache.get('health_probe') == 'ok':
            cache_ok = True
    except Exception as e:
        logger.error(f"Health check Cache probe failed: {e}")

    status_code = status.HTTP_200_OK if db_ok and cache_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response({
        'status': 'healthy' if (db_ok and cache_ok) else 'unhealthy',
        'service': 'ebotar-lite-api',
        'database': 'connected' if db_ok else 'disconnected',
        'cache': 'connected' if cache_ok else 'disconnected',
        'message': 'E-Botar Lite API is running',
    }, status=status_code)


class VersionView(APIView):
    """Version check endpoint."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'version': '3.0.0',
            'api_version': 'v1',
            'system': 'E-Botar Lite (Blockchain Voting System)'
        })


class BrandingView(APIView):
    """Public branding settings."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'institution_name': SystemSettings.get_value('institution_name', 'SURIGAO DEL NORTE'),
            'institution_name_line2': SystemSettings.get_value('institution_name_line2', 'STATE UNIVERSITY'),
            'institution_full_name': 'SURIGAO DEL NORTE STATE UNIVERSITY',
            'app_name': 'E-Botar Lite',
            'institution_logo_url': None,
            'primary_color': SystemSettings.get_value('primary_color', '#0b6e3b'),
            'academic_year': SystemSettings.get_value('academic_year', '2025-2026'),
            'feature_flags': {
                'data_export': True,
                'user_registration': True,
                'google_login': True,
                'staff_preview_disabled_features': True,
            }
        })


class AcademicYearView(APIView):
    """Current academic year getter and setter."""
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffOrSuperUser()]

    def get(self, request):
        academic_year = SystemSettings.get_value('academic_year', default='2025-2026')
        return Response({
            'academic_year': academic_year,
            'display': f'A.Y {academic_year}'
        })

    def put(self, request):
        academic_year = request.data.get('academic_year', '').strip()
        if not academic_year:
            return Response({'error': 'academic_year is required'}, status=status.HTTP_400_BAD_REQUEST)
        SystemSettings.set_value('academic_year', academic_year, description='Academic Year', user=request.user)
        return Response({
            'academic_year': academic_year,
            'display': f'A.Y {academic_year}',
            'message': 'Academic year updated successfully'
        })


class SystemLogListView(APIView):
    """System and security logs for staff and administrators."""
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request):
        log_type = request.query_params.get('type', 'activity')
        paginator = StandardResultsSetPagination()

        if log_type == 'security':
            queryset = SecurityEvent.objects.select_related('user').all()
            page = paginator.paginate_queryset(queryset, request)
            serializer = SecurityEventSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            queryset = ActivityLog.objects.select_related('user').all()
            page = paginator.paginate_queryset(queryset, request)
            serializer = ActivityLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
