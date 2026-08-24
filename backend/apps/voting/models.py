from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.candidates.models import Candidate
from apps.elections.models import SchoolPosition, SchoolElection
from apps.common.core.algorithms import CryptographicAlgorithm
import hmac
import uuid
import secrets


class VoteBlock(models.Model):
    """Append-only blockchain-inspired vote ledger."""

    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='vote_blocks')
    vote_choice = models.ForeignKey('VoteChoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='vote_blocks')
    block_index = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    voter_fingerprint = models.CharField(max_length=64, db_index=True)
    vote_data = models.JSONField()
    previous_hash = models.CharField(max_length=64)
    current_hash = models.CharField(max_length=64, unique=True, db_index=True)
    validator_signature = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voting_voteblock'
        ordering = ['election_id', 'block_index']
        verbose_name = 'Vote Block'
        verbose_name_plural = 'Vote Blocks'
        constraints = [
            models.UniqueConstraint(
                fields=['election', 'block_index'],
                name='unique_vote_block_index_per_election',
            ),
        ]
        indexes = [
            models.Index(fields=['election', 'block_index']),
            models.Index(fields=['election', 'voter_fingerprint']),
        ]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValidationError("Vote blocks are immutable and cannot be updated.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Vote blocks are immutable and cannot be deleted.")

    def __str__(self):
        return f"Block #{self.block_index} ({self.current_hash[:12]}...)"


class VoteReceipt(models.Model):
    """Cryptographic vote receipt for voter verification."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_receipts')
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='receipts')
    receipt_code = models.CharField(max_length=64, unique=True, db_index=True)
    receipt_hash = models.CharField(max_length=64, db_index=True, help_text="SHA-256 hash of receipt for verification")
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'voting_votereceipt'
        unique_together = ['user', 'election']
        ordering = ['-created_at']
        verbose_name = 'Vote Receipt'
        verbose_name_plural = 'Vote Receipts'

    RECEIPT_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    RECEIPT_RAW_LENGTH = 8
    RECEIPT_GROUP_SIZE = 4
    RECEIPT_MAX_GENERATION_ATTEMPTS = 10

    def save(self, *args, **kwargs):
        if not self.receipt_code:
            self.receipt_code = self.generate_unique_receipt_code()
        if not self.receipt_hash:
            self.receipt_hash = self.hash_receipt(self.receipt_code)
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_receipt_code(receipt_code):
        if receipt_code is None:
            return ''
        return ''.join(char.lower() for char in str(receipt_code) if char.isalnum())

    @classmethod
    def format_receipt_code(cls, raw_code):
        normalized_code = cls.normalize_receipt_code(raw_code).upper()
        if not normalized_code:
            return ''
        grouped = [
            normalized_code[index:index + cls.RECEIPT_GROUP_SIZE]
            for index in range(0, len(normalized_code), cls.RECEIPT_GROUP_SIZE)
        ]
        return '-'.join(grouped)

    @classmethod
    def generate_receipt_code(cls):
        random_code = ''.join(
            secrets.choice(cls.RECEIPT_ALPHABET) for _ in range(cls.RECEIPT_RAW_LENGTH)
        )
        return cls.format_receipt_code(random_code)

    @classmethod
    def generate_unique_receipt_code(cls):
        for _ in range(cls.RECEIPT_MAX_GENERATION_ATTEMPTS):
            candidate_code = cls.generate_receipt_code()
            if not cls.objects.filter(receipt_code=candidate_code).exists():
                return candidate_code
        return cls.format_receipt_code(uuid.uuid4().hex[:cls.RECEIPT_RAW_LENGTH])

    @classmethod
    def hash_receipt(cls, receipt_code):
        return CryptographicAlgorithm.sha256_hash(cls.normalize_receipt_code(receipt_code))

    def verify_receipt(self, receipt_code):
        expected_hash = self.hash_receipt(receipt_code)
        return hmac.compare_digest(self.receipt_hash, expected_hash)

    def get_masked_receipt(self):
        if len(self.receipt_code) > 16:
            return f"{self.receipt_code[:8]}...{self.receipt_code[-8:]}"
        return self.receipt_code

    def __str__(self):
        return f"Receipt {self.get_masked_receipt()} for {self.user.username}"


class AnonVote(models.Model):
    """Fully decoupled anonymous vote record."""
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='anon_votes')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, related_name='anon_votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='anon_votes')
    vote_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voting_anonvote'
        ordering = ['-created_at']
        verbose_name = 'Anonymous Vote'
        verbose_name_plural = 'Anonymous Votes'
        indexes = [
            models.Index(fields=['election', 'position', 'candidate']),
        ]

    def save(self, *args, **kwargs):
        if not self.vote_hash:
            hash_data = f"{self.election.id}:{self.position.id}:{self.candidate.id}:{timezone.now().isoformat()}"
            self.vote_hash = CryptographicAlgorithm.sha256_hash(hash_data)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vote for {self.candidate.user.get_full_name()} in {self.position.name}"


class Ballot(models.Model):
    """User ballot submission record."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ballots')
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='ballots')
    receipt = models.OneToOneField(VoteReceipt, on_delete=models.CASCADE, related_name='ballot')
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'voting_ballot'
        unique_together = ['user', 'election']
        ordering = ['-submitted_at']
        verbose_name = 'Ballot'
        verbose_name_plural = 'Ballots'

    def clean(self):
        if not self.election.is_active_now():
            raise ValidationError("This election is not currently active.")
        if Ballot.objects.filter(user=self.user, election=self.election).exclude(pk=self.pk).exists():
            raise ValidationError("You have already submitted a ballot for this election.")

    def __str__(self):
        return f"Ballot by {self.user.username} for {self.election.title}"


class VoteChoice(models.Model):
    """Individual vote choice within a ballot."""
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name='choices')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    anonymized = models.BooleanField(default=False)

    class Meta:
        db_table = 'voting_votechoice'
        unique_together = ['ballot', 'position']
        ordering = ['position__display_order']
        verbose_name = 'Vote Choice'
        verbose_name_plural = 'Vote Choices'

    def anonymize(self):
        if not self.anonymized:
            AnonVote.objects.create(
                election=self.ballot.election,
                position=self.position,
                candidate=self.candidate
            )
            self.anonymized = True
            self.save()

    def __str__(self):
        return f"{self.position.name}: {self.candidate.user.get_full_name()}"
