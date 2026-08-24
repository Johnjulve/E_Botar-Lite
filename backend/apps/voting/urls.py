from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'voting'

router = DefaultRouter()
router.register(r'ballots', views.BallotViewSet, basename='ballot')
router.register(r'receipts', views.VoteReceiptViewSet, basename='receipt')
router.register(r'results', views.ResultsViewSet, basename='results')

urlpatterns = [
    path('voting-status/', views.VotingStatusView.as_view(), name='voting-status'),
    path('', include(router.urls)),
]
