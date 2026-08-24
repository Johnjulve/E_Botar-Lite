"""Throttling helper for sensitive endpoints."""
from rest_framework.exceptions import Throttled
from rest_framework.throttling import ScopedRateThrottle


def enforce_scope_throttle(request, view, scope: str, message: str = None):
    throttle = ScopedRateThrottle()
    throttle.scope = scope
    if not throttle.allow_request(request, view):
        wait = throttle.wait()
        detail = message or f"Request was throttled. Expected available in {int(wait or 1)} seconds."
        raise Throttled(wait=wait, detail=detail)
