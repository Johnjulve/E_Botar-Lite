import logging
from django.db import models, transaction
from django.db.models import Count, OuterRef, Exists
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.accounts.serializers import UserVotingStatusListSerializer
from apps.common.http.pagination import StandardResultsSetPagination
from apps.candidates.models import Candidate
from apps.common.core.algorithms import AggregationAlgorithm, SortingAlgorithm
from apps.common.models import ActivityLog
from apps.common.http.permissions import IsStaffOrSuperUser, IsSuperUser
from apps.common.core.utils import get_client_ip
from apps.elections.models import SchoolElection, SchoolPosition

from .models import Ballot, VoteChoice, VoteReceipt, VoteBlock
from .serializers import (
    BallotSerializer,
    BallotSubmissionSerializer,
    VoteReceiptAuditSerializer,
    VoteReceiptSerializer,
    VoteReceiptVerifySerializer,
)
from .services import VotingDataService
from .vote_ledger import append_vote_blocks_for_ballot, verify_election_vote_chain

logger = logging.getLogger(__name__)


class BallotViewSet(viewsets.ReadOnlyModelViewSet):
    """Voter access to own ballots and ballot submission."""
    queryset = Ballot.objects.select_related('user', 'election', 'receipt').prefetch_related('choices').all()
    serializer_class = BallotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_ballot(self, request):
        election_id = request.query_params.get('election_id')
        if not election_id:
            return Response({'detail': 'election_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ballot = Ballot.objects.get(user=request.user, election_id=election_id)
            serializer = self.get_serializer(ballot)
            return Response(serializer.data)
        except Ballot.DoesNotExist:
            return Response({'detail': 'No ballot found for this election'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        serializer = BallotSubmissionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        election = serializer.validated_data['election']
        votes = serializer.validated_data['votes']
        user = request.user
        client_ip = get_client_ip(request)

        try:
            with transaction.atomic():
                receipt = VoteReceipt.objects.create(
                    user=user,
                    election=election,
                    ip_address=client_ip,
                )

                ballot = Ballot.objects.create(
                    user=user,
                    election=election,
                    receipt=receipt,
                    ip_address=client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                )

                choices_saved = []
                for vote_data in votes:
                    position = SchoolPosition.objects.get(id=vote_data['position_id'])
                    candidate = Candidate.objects.get(
                        id=vote_data['candidate_id'],
                        election=election,
                        position=position,
                        is_active=True
                    )

                    choice = VoteChoice.objects.create(
                        ballot=ballot,
                        position=position,
                        candidate=candidate,
                    )
                    choice.anonymize()
                    choices_saved.append(choice)

                # Append blocks into blockchain ledger
                append_vote_blocks_for_ballot(
                    election_id=election.id,
                    ballot_identifier=str(ballot.pk),
                    receipt_secret=receipt.receipt_hash,
                    user_id=user.id,
                    choices=choices_saved,
                )

                VotingDataService.invalidate_voting_cache(election.id)

                student_id = getattr(getattr(user, 'profile', None), 'student_id', None)
                ActivityLog.objects.create(
                    user=user,
                    action='vote',
                    resource_type='Election',
                    resource_id=election.id,
                    description=f"Student {student_id or user.username} cast vote in election '{election.title}'",
                    ip_address=client_ip,
                    metadata={
                        'election_id': election.id,
                        'receipt_code': receipt.get_masked_receipt(),
                        'positions_voted': len(votes)
                    }
                )

                ballot_serializer = BallotSerializer(ballot)
                return Response({
                    'message': 'Ballot submitted successfully',
                    'ballot': ballot_serializer.data,
                    'receipt_code': receipt.receipt_code
                }, status=status.HTTP_201_CREATED)

        except (SchoolPosition.DoesNotExist, Candidate.DoesNotExist) as e:
            return Response({'detail': f'Invalid position or candidate: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class VoteReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """Vote receipt operations and public cryptographic verification."""
    queryset = VoteReceipt.objects.select_related('user', 'election').all()
    serializer_class = VoteReceiptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_receipts(self, request):
        receipts = self.get_queryset()
        serializer = self.get_serializer(receipts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify(self, request):
        """Verify receipt against blockchain."""
        serializer = VoteReceiptVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_code = serializer.validated_data['receipt_code']
        expected_hash = VoteReceipt.hash_receipt(input_code)

        receipt = VoteReceipt.objects.filter(receipt_hash=expected_hash).select_related('election').first()
        if not receipt:
            return Response({'valid': False, 'detail': 'Invalid receipt code. No matching vote found.'}, status=status.HTTP_404_NOT_FOUND)

        ballot = getattr(receipt, 'ballot', None)
        choices = ballot.choices.select_related('position', 'candidate', 'candidate__user', 'candidate__party') if ballot else []

        votes_data = []
        for choice in choices:
            votes_data.append({
                'position_id': choice.position.id if choice.position else None,
                'position_name': choice.position.name if choice.position else 'Unknown',
                'candidate_id': choice.candidate.id,
                'candidate_name': choice.candidate.user.get_full_name() or 'Unknown',
                'party_name': choice.candidate.party.name if (choice.candidate.party and choice.candidate.party.name) else 'Independent',
            })

        return Response({
            'valid': True,
            'election': {
                'id': receipt.election.id,
                'title': receipt.election.title,
            },
            'voted_at': receipt.created_at,
            'votes': votes_data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsStaffOrSuperUser])
    def audit(self, request):
        """Admin/staff receipt audit list."""
        queryset = VoteReceipt.objects.select_related(
            'user', 'user__profile', 'election'
        ).prefetch_related(
            'ballot', 'ballot__choices', 'ballot__choices__vote_blocks'
        ).all().order_by('-created_at')
        if election_id:
            queryset = queryset.filter(election_id=election_id)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = VoteReceiptAuditSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ResultsViewSet(viewsets.ViewSet):
    """ViewSet for viewing election results and blockchain statistics."""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def election_results(self, request):
        election_id = request.query_params.get('election_id')
        if not election_id:
            return Response({'detail': 'election_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            election = SchoolElection.objects.get(id=election_id)
        except SchoolElection.DoesNotExist:
            return Response({'detail': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)

        user = getattr(request, 'user', None)
        user_is_admin = bool(user and (user.is_staff or user.is_superuser))
        if not election.is_finished() and not user_is_admin and not election.is_active_now():
            return Response({'detail': 'Results will be available once the election starts or finishes.'}, status=status.HTTP_403_FORBIDDEN)

        election_ended = election.is_finished()
        total_voters = VoteReceipt.objects.filter(election=election, user__is_active=True).count()
        total_ballots = Ballot.objects.filter(election=election, user__is_active=True).count()

        if election.election_type == 'university':
            total_eligible = UserProfile.objects.filter(user__is_active=True, user__is_staff=False, user__is_superuser=False).count()
        elif election.election_type == 'department' and election.allowed_department:
            total_eligible = UserProfile.objects.filter(department=election.allowed_department, user__is_active=True, user__is_staff=False, user__is_superuser=False).count()
        else:
            total_eligible = total_voters

        positions_data = []
        positions = election.election_positions.filter(is_enabled=True).order_by('order')

        for ep in positions:
            pos = ep.position
            if not pos:
                continue

            position_votes = list(
                VoteChoice.objects.filter(
                    ballot__election=election,
                    position=pos,
                    ballot__user__is_active=True
                ).values('candidate_id')
            )

            vote_counts = AggregationAlgorithm.aggregate(
                position_votes,
                key_func=lambda v: v.get('candidate_id'),
                operation='count'
            )
            vote_map = {cid: count for cid, count in vote_counts.items() if cid is not None}
            pos_total_votes = sum(vote_map.values())

            candidates = Candidate.objects.filter(election=election, position=pos).select_related('user', 'party')
            candidates_data = []
            for cand in candidates:
                count = vote_map.get(cand.id, 0)
                percentage = VotingDataService.calculate_vote_percentage(count, pos_total_votes)
                candidates_data.append({
                    'candidate_id': cand.id,
                    'candidate_name': cand.user.get_full_name() or cand.user.username,
                    'party': cand.party.name if (cand.party and cand.party.name) else None,
                    'vote_count': count,
                    'percentage': percentage,
                    'is_winner': False,
                    'rank': None
                })

            candidates_data = SortingAlgorithm.quicksort(
                candidates_data,
                key=lambda c: c['vote_count'],
                reverse=True
            )
            for idx, c_data in enumerate(candidates_data, start=1):
                c_data['rank'] = idx
                c_data['is_winner'] = election_ended and idx == 1 and c_data['vote_count'] > 0

            positions_data.append({
                'position_id': pos.id,
                'position_name': pos.name,
                'total_votes': pos_total_votes,
                'candidates': candidates_data
            })

        return Response({
            'election_id': election.id,
            'election_title': election.title,
            'election_ended': election_ended,
            'is_active': election.is_active_now(),
            'total_voters': total_voters,
            'total_ballots': total_ballots,
            'total_eligible_students': total_eligible,
            'positions': positions_data
        })

    @action(detail=False, methods=['get'])
    def my_vote_status(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        election_id = request.query_params.get('election_id')
        if not election_id:
            return Response({'detail': 'election_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            election = SchoolElection.objects.get(id=election_id)
            receipt = VoteReceipt.objects.filter(user=request.user, election=election).first()
            return Response({
                'election_id': election.id,
                'election_title': election.title,
                'has_voted': receipt is not None,
                'voted_at': receipt.created_at if receipt else None,
                'receipt_code': receipt.get_masked_receipt() if receipt else None
            })
        except SchoolElection.DoesNotExist:
            return Response({'detail': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        election_id = request.query_params.get('election_id')
        if not election_id:
            return Response({'detail': 'election_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        stats = VotingDataService.get_election_statistics(election_id)
        return Response(stats)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsStaffOrSuperUser])
    def ledger_integrity(self, request):
        """Recompute VoteBlock hashes and chain linkage for tamper validation."""
        election_id = request.query_params.get('election_id')
        if not election_id:
            return Response({'detail': 'election_id query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            election = SchoolElection.objects.get(id=election_id)
        except SchoolElection.DoesNotExist:
            return Response({'detail': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)

        ledger_ok, errors = verify_election_vote_chain(election.id)
        block_total = VoteBlock.objects.filter(election_id=election.id).count()

        ActivityLog.objects.create(
            user=request.user,
            action='read',
            resource_type='VoteLedgerIntegrity',
            resource_id=election.id,
            description=f"Ledger integrity verification for '{election.title}': {'OK' if ledger_ok else 'FAILED'}",
            ip_address=get_client_ip(request),
        )

        return Response({
            'election_id': election.id,
            'election_title': election.title,
            'ledger_ok': ledger_ok,
            'block_count': block_total,
            'errors': errors,
        })


class VotingStatusView(generics.ListAPIView):
    serializer_class = UserVotingStatusListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrSuperUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        election_id = self.request.query_params.get('election_id')
        if not election_id:
            return UserProfile.objects.none()

        voted_subquery = Ballot.objects.filter(
            user_id=models.OuterRef('user_id'),
            election_id=election_id,
        )
        return UserProfile.objects.select_related('user', 'department', 'course').filter(
            user__is_active=True,
            user__is_staff=False,
            user__is_superuser=False,
        ).annotate(has_voted=models.Exists(voted_subquery))
