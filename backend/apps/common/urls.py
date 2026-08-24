from django.urls import path
from .views import health_check, VersionView, BrandingView, AcademicYearView, SystemLogListView

app_name = 'common'

urlpatterns = [
    path('health/', health_check, name='health'),
    path('version/', VersionView.as_view(), name='version'),
    path('branding/', BrandingView.as_view(), name='branding'),
    path('academic-year/', AcademicYearView.as_view(), name='academic-year'),
    path('system-logs/', SystemLogListView.as_view(), name='system-logs'),
]
