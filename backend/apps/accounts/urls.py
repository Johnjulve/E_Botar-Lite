from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    CurrentUserView,
    UserProfileViewSet,
    DepartmentListView,
    CourseListView,
    ProgramViewSet,
    UserManagementViewSet,
    user_count_view,
    student_roster_preview,
    student_roster_import,
)

app_name = 'accounts'

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'users', UserManagementViewSet, basename='user')

urlpatterns = [
    # Auth endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('user-counts/', user_count_view, name='user-counts'),

    # Public program helpers
    path('departments/', DepartmentListView.as_view(), name='departments-list'),
    path('courses/', CourseListView.as_view(), name='courses-list'),

    # Roster Sync Endpoints
    path('students/roster-preview/', student_roster_preview, name='student-roster-preview'),
    path('students/roster-execute/', student_roster_import, name='student-roster-import'),

    # ViewSet routes
    path('', include(router.urls)),
]
