"""Public URL helper for FileField / ImageField instances."""
from typing import Optional
from django.conf import settings


def _is_absolute_url(value: str) -> bool:
    if not value:
        return False
    lower = value.lower()
    return lower.startswith("http://") or lower.startswith("https://")


def absolute_file_url(file_field, request=None) -> Optional[str]:
    if not file_field:
        return None

    try:
        raw_url = file_field.url
    except (ValueError, AttributeError):
        return None

    if not raw_url:
        return None

    if _is_absolute_url(raw_url):
        return raw_url

    backend_base = getattr(settings, "BACKEND_BASE_URL", None)
    if backend_base:
        return f"{backend_base.rstrip('/')}/{raw_url.lstrip('/')}"

    if request is not None:
        try:
            return request.build_absolute_uri(raw_url)
        except Exception:
            scheme = getattr(request, "scheme", None)
            host_getter = getattr(request, "get_host", None)
            if scheme and callable(host_getter):
                return f"{scheme}://{host_getter()}{raw_url}"

    return raw_url
