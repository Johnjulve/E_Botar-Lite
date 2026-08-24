"""Common serializers."""
from rest_framework import serializers
from .models import ActivityLog, SecurityEvent, SystemSettings


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='System')
    full_name = serializers.CharField(source='user.get_full_name', read_only=True, default='')

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'username', 'full_name', 'action', 'resource_type', 'resource_id', 'description', 'ip_address', 'metadata', 'created_at']


class SecurityEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='Anonymous')

    class Meta:
        model = SecurityEvent
        fields = ['id', 'user', 'username', 'event_type', 'severity', 'description', 'ip_address', 'user_agent', 'metadata', 'created_at']


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ['id', 'key', 'value', 'description', 'updated_at']
