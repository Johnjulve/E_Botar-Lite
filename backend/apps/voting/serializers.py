from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VoteReceipt, AnonVote, Ballot, VoteChoice
from apps.candidates.serializers import CandidateListSerializer
from apps.elections.serializers import (
    SchoolPositionMinimalSerializer,
    SchoolElectionMinimalSerializer,
)


class VoteReceiptSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    election = SchoolElectionMinimalSerializer(read_only=True)
    masked_receipt_code = serializers.CharField(source='get_masked_receipt', read_only=True)

    class Meta:
        model = VoteReceipt
        fields = [
            'id', 'user', 'user_name', 'election',
            'masked_receipt_code', 'created_at',
        ]
        read_only_fields = fields


class VoteReceiptVerifySerializer(serializers.Serializer):
    receipt_code = serializers.CharField(max_length=64)

    def validate_receipt_code(self, value):
        normalized = VoteReceipt.normalize_receipt_code(value)
        if len(normalized) < VoteReceipt.RECEIPT_RAW_LENGTH:
            raise serializers.ValidationError("Invalid receipt code format")
        return value.strip()


class VoteChoiceSerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source='position.name', read_only=True)
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)

    class Meta:
        model = VoteChoice
        fields = ['id', 'position', 'position_name', 'candidate', 'candidate_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class BallotSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    election_title = serializers.CharField(source='election.title', read_only=True)
    choices = VoteChoiceSerializer(many=True, read_only=True)
    receipt_code = serializers.CharField(source='receipt.receipt_code', read_only=True)

    class Meta:
        model = Ballot
        fields = [
            'id', 'user', 'user_name', 'election', 'election_title',
            'receipt', 'receipt_code', 'choices', 'submitted_at'
        ]
        read_only_fields = ['id', 'receipt', 'submitted_at']


class BallotSubmissionSerializer(serializers.Serializer):
    election_id = serializers.IntegerField()
    votes = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        help_text="List of vote dictionaries with 'position_id' and 'candidate_id'"
    )

    def validate_votes(self, value):
        for vote in value:
            if 'position_id' not in vote or 'candidate_id' not in vote:
                raise serializers.ValidationError(
                    "Each vote must contain 'position_id' and 'candidate_id'"
                )
        return value

    def validate(self, data):
        from apps.elections.models import SchoolElection
        try:
            election = SchoolElection.objects.get(id=data['election_id'])
        except SchoolElection.DoesNotExist:
            raise serializers.ValidationError({'election_id': 'Election not found'})

        user = self.context['request'].user
        if not (user.is_staff or user.is_superuser):
            if not election.is_active_now():
                raise serializers.ValidationError({'election_id': 'This election is not currently active for voting.'})
            if not election.is_user_eligible(user):
                raise serializers.ValidationError({'election_id': 'You are not eligible to vote in this election.'})

        if Ballot.objects.filter(user=user, election=election).exists():
            raise serializers.ValidationError({'election_id': 'You have already voted in this election.'})

        data['election'] = election
        return data


class VoteReceiptAuditSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(source='user.profile.student_id', read_only=True, default='')
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    election_title = serializers.CharField(source='election.title', read_only=True)
    masked_receipt_code = serializers.CharField(source='get_masked_receipt', read_only=True)
    positions_voted = serializers.SerializerMethodField()

    class Meta:
        model = VoteReceipt
        fields = [
            'id', 'user', 'username', 'user_name', 'student_id',
            'election', 'election_title', 'masked_receipt_code',
            'positions_voted', 'created_at', 'ip_address'
        ]

    def get_positions_voted(self, obj):
        try:
            return obj.ballot.choices.count() if hasattr(obj, 'ballot') else 0
        except Exception:
            return 0
