"""Custom rate limiting classes for different API endpoints.

Provides granular rate limiting for different types of operations:
- Authentication endpoints: stricter limits to prevent brute force
- Voting endpoints: moderate limits to prevent abuse
- General API: standard limits for normal usage
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Stricter rate limiting for authentication endpoints."""
    scope = "auth"
    rate = "5/hour"  # 5 attempts per hour for login


class VoteRateThrottle(UserRateThrottle):
    """Rate limiting for voting to prevent abuse."""
    scope = "vote"
    rate = "10/hour"  # 10 votes per hour per user


class MenuUploadRateThrottle(UserRateThrottle):
    """Rate limiting for menu uploads (admin only)."""
    scope = "menu_upload"
    rate = "20/hour"  # 20 menu uploads per hour


class BurstRateThrottle(AnonRateThrottle):
    """Burst protection for all endpoints."""
    scope = "burst"
    rate = "30/minute"  # 30 requests per minute for anonymous users
