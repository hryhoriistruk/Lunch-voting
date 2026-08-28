"""
Backward-compatibility support for mobile app clients.

The mobile app always sends its build version in the ``X-App-Version``
HTTP header (e.g. ``X-App-Version: 1.4.2``). Some users are still running
old builds that expect an older, flatter response shape from a couple of
endpoints (current-day menu, current-day results). Rather than branching
on version strings inside views, we expose a small, testable helper that
answers a single question: "is this request from a legacy client?".

Views/serializers that need to differ between versions ask
``request.version_info.is_legacy`` (see below) instead of parsing headers
themselves - this keeps the branching logic in one place.
"""
from dataclasses import dataclass

from rest_framework.versioning import BaseVersioning

from django.conf import settings


def _parse_version(value: str) -> tuple:
    """Turn '1.4.2' into (1, 4, 2) for safe numeric comparison.

    Falls back to (0,) for garbage/missing input so unknown/old clients
    are always treated as legacy rather than crashing the request.
    """
    if not value:
        return (0,)
    parts = []
    for chunk in value.strip().split("."):
        try:
            parts.append(int(chunk))
        except ValueError:
            break
    return tuple(parts) or (0,)


@dataclass(frozen=True)
class VersionInfo:
    raw: str
    is_legacy: bool


class AppBuildVersioning(BaseVersioning):
    """Reads the app build version from the ``X-App-Version`` header.

    This does not change URL routing (unlike DRF's URL/namespace
    versioning schemes) - it just annotates the request so views and
    serializers can pick the right response shape. Missing header is
    treated as legacy, which is the safe default: an old, un-updated
    client wouldn't have known to send the header in the first place.
    """

    header = "X-App-Version"

    def determine_version(self, request, *args, **kwargs):
        raw_value = request.META.get(settings.APP_VERSION_HEADER, "")
        breakpoint_version = _parse_version(settings.APP_VERSION_BREAKPOINT)
        is_legacy = _parse_version(raw_value) < breakpoint_version
        request.version_info = VersionInfo(raw=raw_value, is_legacy=is_legacy)
        return raw_value or None
