"""Utility functions for logging and security"""
import logging
from ..models import ActivityLog, SecurityEvent

logger = logging.getLogger(__name__)


def log_activity(user, action, resource_type, resource_id=None, description='', ip_address=None, metadata=None):
    """Log user activity into ActivityLog."""
    try:
        from django.db import OperationalError, ProgrammingError
        ActivityLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            metadata=metadata or {}
        )
    except (OperationalError, ProgrammingError) as e:
        logger.debug(f"ActivityLog table not available, skipping log: {e}")
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")


def log_security_event(user, event_type, severity, description, ip_address=None, user_agent='', metadata=None):
    """Log security event into SecurityEvent."""
    try:
        from django.db import OperationalError, ProgrammingError
        SecurityEvent.objects.create(
            user=user,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
    except (OperationalError, ProgrammingError) as e:
        logger.debug(f"SecurityEvent table not available, skipping log: {e}")
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")


def get_client_ip(request):
    """Extract client IP from X-Forwarded-For or REMOTE_ADDR."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
