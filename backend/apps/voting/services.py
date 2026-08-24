"""
Voting Data Services
Provides calculations, statistics, and caching for voting operations.
"""

from django.core.cache import cache
from django.db.models import Count
from apps.common.core.algorithms import CryptographicAlgorithm
from .models import Ballot, VoteChoice, VoteReceipt
from apps.candidates.models import Candidate
from apps.elections.models import SchoolElection, SchoolPosition
from apps.accounts.models import UserProfile


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
