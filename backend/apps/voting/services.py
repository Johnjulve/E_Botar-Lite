"""
Voting Data Services
Provides calculations, statistics, and caching for voting operations.
"""

from django.core.cache import cache
from django.db.models import Count

from .models import Ballot, VoteChoice, VoteReceipt
from apps.candidates.models import Candidate
from apps.elections.models import SchoolElection, SchoolPosition
from apps.accounts.models import UserProfile
from django.db import transaction
from apps.common.core.utils import get_client_ip
from .vote_ledger import append_vote_blocks_for_ballot
from apps.common.models import ActivityLog


class VotingDataService:
    """Service class for voting data operations and stats."""

    @staticmethod
    def calculate_vote_percentage(votes, total_votes):
        if not total_votes or total_votes == 0:
            return 0.0
        return round((votes / total_votes) * 100, 2)

    @staticmethod
    def invalidate_voting_cache(election_id=None):
        """Invalidate voting cache keys."""
        try:
            cache.clear()
        except Exception:
            pass

    @staticmethod
    def get_election_statistics(election_id):
        """Compute summary statistics for an election."""
        election = SchoolElection.objects.get(id=election_id)
        total_voters = VoteReceipt.objects.filter(election=election, user__is_active=True).count()
        total_votes_cast = VoteChoice.objects.filter(ballot__election=election, ballot__user__is_active=True).count()

        if election.election_type == 'university':
            total_registered = UserProfile.objects.filter(user__is_active=True, user__is_staff=False, user__is_superuser=False).count()
        elif election.election_type == 'department' and election.allowed_department:
            total_registered = UserProfile.objects.filter(department=election.allowed_department, user__is_active=True, user__is_staff=False, user__is_superuser=False).count()
        else:
            total_registered = total_voters

        turnout = round((total_voters / total_registered * 100), 2) if total_registered > 0 else 0.0

        votes_by_position = list(
            VoteChoice.objects.filter(ballot__election=election, ballot__user__is_active=True)
            .values('position_id', 'position__name')
            .annotate(vote_count=Count('id'))
            .order_by('position__display_order')
        )

        return {
            'unique_voters': total_voters,
            'total_votes_cast': total_votes_cast,
            'total_registered_voters': total_registered,
            'turnout_percentage': turnout,
            'votes_by_position': votes_by_position
        }


class BallotSubmissionService:
    """Service to handle atomic ballot submissions with concurrency locks."""

    @staticmethod
    def submit_ballot(user, election, votes_data, request):
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

        with transaction.atomic():
            # Lock the user profile to strictly prevent double-voting anomalies under load
            UserProfile.objects.select_for_update().get(user=user)

            if Ballot.objects.filter(user=user, election=election).exists():
                raise ValueError("You have already submitted a ballot for this election.")

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
                user_agent=user_agent,
            )

            choices_saved = []
            for vote_data in votes_data:
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
                    'positions_voted': len(votes_data)
                }
            )

            return ballot, receipt
