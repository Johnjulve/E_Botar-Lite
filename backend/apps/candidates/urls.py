from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'candidates'

router = DefaultRouter()
router.register(r'candidates', views.CandidateViewSet, basename='candidate')

urlpatterns = [
    path('', include(router.urls)),
]
