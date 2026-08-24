from rest_framework import serializers
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.common.files.file_urls import absolute_file_url

from .models import Candidate
from apps.elections.serializers import (
    SchoolPositionSerializer,
    SchoolPositionMinimalSerializer,
    PartySerializer,
    PartyMinimalSerializer,
    SchoolElectionListSerializer,
    SchoolElectionMinimalSerializer,
)


class CandidateUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    student_id = serializers.CharField(source='profile.student_id', read_only=True, default='')
    course_code = serializers.SerializerMethodField()
    year_level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'student_id', 'course_code', 'year_level']

    def get_course_code(self, obj):
        try:
            return obj.profile.course.code if obj.profile.course else None
        except UserProfile.DoesNotExist:
            return None

    def get_year_level(self, obj):
        try:
            return obj.profile.year_level
        except UserProfile.DoesNotExist:
            return None


class CandidateListSerializer(serializers.ModelSerializer):
    user = CandidateUserSerializer(read_only=True)
    position = SchoolPositionMinimalSerializer(read_only=True)
    party = PartyMinimalSerializer(read_only=True)
    election = SchoolElectionMinimalSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'user', 'position', 'election',
            'party', 'manifesto', 'photo', 'photo_url', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_photo_url(self, obj):
        return absolute_file_url(obj.photo, self.context.get('request'))


class CandidateCompactSerializer(serializers.ModelSerializer):
    user = CandidateUserSerializer(read_only=True)
    position = SchoolPositionMinimalSerializer(read_only=True)
    party = PartyMinimalSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'user', 'position', 'party']


class CandidateDetailSerializer(serializers.ModelSerializer):
    user = CandidateUserSerializer(read_only=True)
    position = SchoolPositionSerializer(read_only=True)
    party = PartySerializer(read_only=True)
    election = SchoolElectionListSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'user', 'position', 'election',
            'party', 'manifesto', 'photo', 'photo_url', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_photo_url(self, obj):
        return absolute_file_url(obj.photo, self.context.get('request'))


class CandidateCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Admin direct Candidate creation and update."""
    user_id = serializers.IntegerField(write_only=True)
    position_id = serializers.IntegerField(write_only=True)
    election_id = serializers.IntegerField(write_only=True)
    party_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Candidate
        fields = [
            'id', 'user_id', 'position_id', 'election_id', 'party_id',
            'manifesto', 'photo', 'is_active'
        ]

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        position_id = validated_data.pop('position_id')
        election_id = validated_data.pop('election_id')
        party_id = validated_data.pop('party_id', None)

        candidate, _ = Candidate.objects.update_or_create(
            user_id=user_id,
            position_id=position_id,
            election_id=election_id,
            defaults={
                'party_id': party_id,
                **validated_data
            }
        )
        return candidate

    def update(self, instance, validated_data):
        if 'user_id' in validated_data:
            instance.user_id = validated_data.pop('user_id')
        if 'position_id' in validated_data:
            instance.position_id = validated_data.pop('position_id')
        if 'election_id' in validated_data:
            instance.election_id = validated_data.pop('election_id')
        if 'party_id' in validated_data:
            instance.party_id = validated_data.pop('party_id')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
