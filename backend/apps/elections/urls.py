from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'elections'

router = DefaultRouter()
router.register(r'parties', views.PartyViewSet, basename='party')
router.register(r'positions', views.SchoolPositionViewSet, basename='position')
router.register(r'elections', views.SchoolElectionViewSet, basename='election')
router.register(r'election-positions', views.ElectionPositionViewSet, basename='election-position')

urlpatterns = [
    path('', include(router.urls)),
]
