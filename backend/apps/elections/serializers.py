from django.utils import timezone
from rest_framework import serializers
from apps.accounts.serializers import DepartmentSerializer
from .models import Party, SchoolPosition, SchoolElection, ElectionPosition


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'name', 'description', 'logo', 'color', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PartyMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'name', 'color']


class SchoolPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolPosition
        fields = ['id', 'name', 'description', 'display_order', 'max_candidates', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SchoolPositionMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolPosition
        fields = ['id', 'name', 'display_order']


class ElectionPositionSerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source='position.name', read_only=True)
    position_description = serializers.CharField(source='position.description', read_only=True)

    class Meta:
        model = ElectionPosition
        fields = ['id', 'election', 'position', 'position_name', 'position_description', 'order', 'is_enabled']


class SchoolElectionListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    is_active_now = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    is_finished = serializers.SerializerMethodField()
    allowed_department_details = DepartmentSerializer(source='allowed_department', read_only=True)
    total_positions = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = SchoolElection
        fields = [
            'id', 'title', 'election_type', 'allowed_department', 'allowed_department_details',
            'start_year', 'end_year', 'description', 'start_date', 'end_date',
            'is_active', 'is_paused', 'status', 'is_active_now', 'is_upcoming', 'is_finished',
            'total_positions', 'total_votes', 'created_at'
        ]

    def get_status(self, obj):
        now = timezone.now()
        if getattr(obj, 'is_paused', False) and obj.is_active and obj.start_date <= now <= obj.end_date:
            return 'paused'
        if obj.is_active_now():
            return 'ongoing'
        if obj.is_upcoming():
            return 'upcoming'
        if obj.is_finished():
            return 'finished'
        return 'inactive'

    def get_is_active_now(self, obj):
        return obj.is_active_now()

    def get_is_upcoming(self, obj):
        return obj.is_upcoming()

    def get_is_finished(self, obj):
        return obj.is_finished()

    def get_total_positions(self, obj):
        return obj.election_positions.filter(is_enabled=True).count()

    def get_total_votes(self, obj):
        try:
            return obj.receipts.count()
        except Exception:
            return 0


class SchoolElectionMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolElection
        fields = ['id', 'title', 'election_type']


class SchoolElectionDetailSerializer(SchoolElectionListSerializer):
    election_positions = ElectionPositionSerializer(many=True, read_only=True)

    class Meta(SchoolElectionListSerializer.Meta):
        fields = SchoolElectionListSerializer.Meta.fields + ['election_positions']


class SchoolElectionCreateUpdateSerializer(serializers.ModelSerializer):
    position_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = SchoolElection
        fields = [
            'id', 'title', 'election_type', 'allowed_department',
            'start_year', 'end_year', 'description',
            'start_date', 'end_date', 'is_active', 'is_paused',
            'position_ids'
        ]

    def create(self, validated_data):
        position_ids = validated_data.pop('position_ids', [])
        validated_data['created_by'] = self.context['request'].user
        election = SchoolElection.objects.create(**validated_data)

        for order, pos_id in enumerate(position_ids):
            pos = SchoolPosition.objects.filter(id=pos_id).first()
            if pos:
                ElectionPosition.objects.create(
                    election=election,
                    position=pos,
                    order=order,
                    is_enabled=True
                )
        return election

    def update(self, instance, validated_data):
        position_ids = validated_data.pop('position_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if position_ids is not None:
            instance.election_positions.all().delete()
            for order, pos_id in enumerate(position_ids):
                pos = SchoolPosition.objects.filter(id=pos_id).first()
                if pos:
                    ElectionPosition.objects.create(
                        election=instance,
                        position=pos,
                        order=order,
                        is_enabled=True
                    )
        return instance
