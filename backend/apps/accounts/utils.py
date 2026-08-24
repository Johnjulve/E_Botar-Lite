"""Helpers for staff and student profile management."""
import re
from .models import UserProfile


def parse_year_level_value(raw):
    """Extract numeric year level from string."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = re.search(r'\d+', s)
    if m:
        return int(m.group(0))
    return None


def staff_can_manage_student_profile(actor, target_profile):
    """Staff permission check based on year level."""
    if actor.is_superuser:
        return True
    if not getattr(actor, 'is_staff', False):
        return False

    target_user = target_profile.user
    if target_user.is_superuser or target_user.is_staff:
        return False

    try:
        staff_profile = actor.profile
    except UserProfile.DoesNotExist:
        return False

    staff_y = parse_year_level_value(getattr(staff_profile, 'year_level', None))
    if staff_y is None:
        return False

    target_y = parse_year_level_value(getattr(target_profile, 'year_level', None))
    if target_y is None:
        return True

    return target_y <= staff_y
