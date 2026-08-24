import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.models import ActivityLog
from apps.common.http.permissions import IsStaffOrSuperUser, IsSuperUser
from apps.common.core.utils import get_client_ip

from .models import ElectionPosition, Party, SchoolElection, SchoolPosition
from .serializers import (
    ElectionPositionSerializer,
    PartySerializer,
    SchoolElectionCreateUpdateSerializer,
    SchoolElectionDetailSerializer,
    SchoolElectionListSerializer,
    SchoolPositionSerializer,
)

logger = logging.getLogger(__name__)


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsStaffOrSuperUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user.is_staff or self.request.user.is_superuser) and self.action == 'list':
            qs = qs.filter(is_active=True)
        return qs


class SchoolPositionViewSet(viewsets.ModelViewSet):
    queryset = SchoolPosition.objects.all()
    serializer_class = SchoolPositionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsStaffOrSuperUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user.is_staff or self.request.user.is_superuser) and self.action == 'list':
            qs = qs.filter(is_active=True)
        return qs


class SchoolElectionViewSet(viewsets.ModelViewSet):
    queryset = SchoolElection.objects.all().prefetch_related('election_positions__position')

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'active', 'upcoming', 'finished']:
            return [AllowAny()]
        return [IsStaffOrSuperUser()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SchoolElectionCreateUpdateSerializer
        if self.action == 'retrieve':
            return SchoolElectionDetailSerializer
        return SchoolElectionListSerializer

    def perform_create(self, serializer):
        election = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action='create',
            resource_type='Election',
            resource_id=election.id,
            description=f"Admin {self.request.user.username} created election '{election.title}'",
            ip_address=get_client_ip(self.request),
        )

    def perform_update(self, serializer):
        election = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action='update',
            resource_type='Election',
            resource_id=election.id,
            description=f"Admin {self.request.user.username} updated election '{election.title}'",
            ip_address=get_client_ip(self.request),
        )

    def perform_destroy(self, instance):
        title = instance.title
        election_id = instance.id
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action='delete',
            resource_type='Election',
            resource_id=election_id,
            description=f"Admin {self.request.user.username} deleted election '{title}'",
            ip_address=get_client_ip(self.request),
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        now = timezone.now()
        active_elections = self.get_queryset().filter(is_active=True, start_date__lte=now, end_date__gte=now)
        serializer = self.get_serializer(active_elections, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        now = timezone.now()
        upcoming_elections = self.get_queryset().filter(is_active=True, start_date__gt=now)
        serializer = self.get_serializer(upcoming_elections, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def finished(self, request):
        now = timezone.now()
        finished_elections = self.get_queryset().filter(end_date__lt=now)
        serializer = self.get_serializer(finished_elections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrSuperUser])
    def toggle_pause(self, request, pk=None):
        election = self.get_object()
        election.is_paused = not election.is_paused
        election.save()
        return Response({'is_paused': election.is_paused, 'title': election.title})


class ElectionPositionViewSet(viewsets.ModelViewSet):
    queryset = ElectionPosition.objects.all()
    serializer_class = ElectionPositionSerializer
    permission_classes = [IsStaffOrSuperUser]
