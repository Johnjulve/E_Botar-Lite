import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.models import ActivityLog
from apps.common.http.permissions import IsStaffOrSuperUser
from apps.common.core.utils import get_client_ip

from .models import Candidate
from .serializers import (
    CandidateCompactSerializer,
    CandidateCreateUpdateSerializer,
    CandidateDetailSerializer,
    CandidateListSerializer,
)

logger = logging.getLogger(__name__)


class CandidateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing candidates.
    Public: read-only access (list, retrieve, by_election).
    Staff/Admin: direct CRUD access (create, update, delete).
    """
    queryset = Candidate.objects.select_related('user', 'user__profile', 'position', 'election', 'party').all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'by_election']:
            return [AllowAny()]
        return [IsStaffOrSuperUser()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CandidateCreateUpdateSerializer
        compact = str(self.request.query_params.get('compact', 'false')).lower() == 'true'
        if compact and self.action in ['list', 'by_election']:
            return CandidateCompactSerializer
        if self.action == 'retrieve':
            return CandidateDetailSerializer
        return CandidateListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        election_id = self.request.query_params.get('election', None) or self.request.query_params.get('election_id', None)
        if election_id:
            queryset = queryset.filter(election_id=election_id)

        position_id = self.request.query_params.get('position', None) or self.request.query_params.get('position_id', None)
        if position_id:
            queryset = queryset.filter(position_id=position_id)

        party_id = self.request.query_params.get('party', None) or self.request.query_params.get('party_id', None)
        if party_id:
            queryset = queryset.filter(party_id=party_id)

        # Filter active only for non-staff
        if not (self.request.user and (self.request.user.is_staff or self.request.user.is_superuser)):
            queryset = queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        candidate = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action='create',
            resource_type='Candidate',
            resource_id=candidate.id,
            description=f"Admin {self.request.user.username} added candidate {candidate.user.get_full_name()} for position {candidate.position.name}",
            ip_address=get_client_ip(self.request),
        )

    def perform_update(self, serializer):
        candidate = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action='update',
            resource_type='Candidate',
            resource_id=candidate.id,
            description=f"Admin {self.request.user.username} updated candidate {candidate.user.get_full_name()}",
            ip_address=get_client_ip(self.request),
        )

    def perform_destroy(self, instance):
        name = instance.user.get_full_name()
        cand_id = instance.id
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action='delete',
            resource_type='Candidate',
            resource_id=cand_id,
            description=f"Admin {self.request.user.username} removed candidate {name}",
            ip_address=get_client_ip(self.request),
        )

    @action(detail=False, methods=['get'])
    def by_election(self, request):
        election_id = request.query_params.get('election_id') or request.query_params.get('election')
        if not election_id:
            return Response(
                {'detail': 'election_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        candidates = self.get_queryset().filter(election_id=election_id)
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrSuperUser])
    def toggle_active(self, request, pk=None):
        candidate = self.get_object()
        candidate.is_active = not candidate.is_active
        candidate.save()
        return Response({'is_active': candidate.is_active})
