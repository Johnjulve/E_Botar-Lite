from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import UserProfile, Program
from apps.elections.models import SchoolElection, SchoolPosition, ElectionPosition, Party
from apps.candidates.models import Candidate
from apps.voting.models import Ballot, VoteChoice, VoteReceipt, VoteBlock
from apps.voting.vote_ledger import append_vote_blocks_for_ballot, verify_election_vote_chain
from apps.voting.services import VotingDataService
from django.db import transaction


class BlockchainVotingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='student1', password='password123', first_name='Student', last_name='One')
        self.user2 = User.objects.create_user(username='student2', password='password123', first_name='Student', last_name='Two')
        self.profile1 = UserProfile.objects.create(user=self.user1, student_id='2024-00001')
        self.profile2 = UserProfile.objects.create(user=self.user2, student_id='2024-00002')

        now = timezone.now()
        self.election = SchoolElection.objects.create(
            title='USC Test Election',
            election_type='university',
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=5),
            is_active=True
        )

        self.position = SchoolPosition.objects.create(name='President', display_order=1)
        self.el_pos = ElectionPosition.objects.create(election=self.election, position=self.position, order=1, is_enabled=True)

        self.party = Party.objects.create(name='Test Party', color='#0b6e3b')
        self.candidate = Candidate.objects.create(
            user=self.user1,
            position=self.position,
            election=self.election,
            party=self.party,
            manifesto='A great student leader.',
            is_active=True
        )

    def test_direct_candidate_creation(self):
        """Test admin can directly create candidate without candidate applications."""
        self.assertEqual(Candidate.objects.count(), 1)
        candidate = Candidate.objects.get(pk=self.candidate.pk)
        self.assertEqual(candidate.user.username, 'student1')
        self.assertEqual(candidate.position.name, 'President')

    def test_blockchain_vote_append_and_integrity(self):
        """Test append-only blockchain vote blocks and hash chain verification."""
        with transaction.atomic():
            receipt = VoteReceipt.objects.create(user=self.user2, election=self.election)
            ballot = Ballot.objects.create(user=self.user2, election=self.election, receipt=receipt)
            choice = VoteChoice.objects.create(ballot=ballot, position=self.position, candidate=self.candidate)

            blocks = append_vote_blocks_for_ballot(
                election_id=self.election.id,
                ballot_identifier=str(ballot.pk),
                receipt_secret=receipt.receipt_hash,
                user_id=self.user2.id,
                choices=[choice]
            )

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].block_index, 1)
        self.assertEqual(blocks[0].previous_hash, '0' * 64)

        # Integrity verification passes
        is_valid, errors = verify_election_vote_chain(self.election.id)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_vote_receipt_verification(self):
        """Test cryptographic receipt verification."""
        receipt = VoteReceipt.objects.create(user=self.user2, election=self.election)
        self.assertTrue(receipt.verify_receipt(receipt.receipt_code))
        self.assertFalse(receipt.verify_receipt('INVALID-CODE-9999'))
