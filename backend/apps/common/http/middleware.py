"""Middleware for platform host handling and security logging."""
import logging
import os
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from ..core.utils import get_client_ip, log_security_event

logger = logging.getLogger(__name__)


class DynamicAllowedHostsMiddleware(MiddlewareMixin):
    """Middleware to dynamically handle ALLOWED_HOSTS on hosting platforms."""
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        if '*' in settings.ALLOWED_HOSTS:
            return None
        if host not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS.append(host)
        return None


class SecurityLoggingMiddleware(MiddlewareMixin):
    """Log security-relevant requests."""
    def process_request(self, request):
        request.security_meta = {
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
        }
        return None
