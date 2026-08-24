"""Upload path helpers for avatars and candidate photos."""
import os
from typing import Optional
from django.utils.text import slugify

PROFILE_PHOTO_FOLDER = "profile_photos"
CANDIDATE_PHOTO_FOLDER = "candidate_photos"


def safe_extension(filename: Optional[str]) -> str:
    """Return lowercased extension with leading dot."""
    if not filename:
        return ""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def user_filename_identifier(user) -> str:
    """Stable identifier for filenames."""
    if user is None:
        return "user"
    profile = getattr(user, "profile", None)
    if profile is not None:
        student_id = (getattr(profile, "student_id", "") or "").strip()
        if student_id:
            return student_id
    username = (getattr(user, "username", "") or "").strip()
    if username:
        return slugify(username) or username
    pk = getattr(user, "pk", None)
    if pk:
        return str(pk)
    return "user"


def avatar_upload_path(instance, filename: str) -> str:
    identifier = user_filename_identifier(getattr(instance, 'user', None))
    return f"{PROFILE_PHOTO_FOLDER}/{identifier}{safe_extension(filename)}"


def candidate_photo_upload_path(instance, filename: str) -> str:
    identifier = user_filename_identifier(getattr(instance, 'user', None))
    return f"{CANDIDATE_PHOTO_FOLDER}/{identifier}{safe_extension(filename)}"
