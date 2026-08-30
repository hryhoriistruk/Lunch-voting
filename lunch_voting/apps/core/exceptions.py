"""A single, predictable error response shape for the whole API.

Without this, DRF's default handler returns different payload shapes for
validation errors, permission errors, etc. Front-end/mobile clients
benefit from always seeing ``{"detail": ..., "errors": {...}}``.
"""
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


class BusinessLogicError(APIException):
    """Base class for business logic errors."""
    status_code = 400
    default_detail = "Business logic error occurred."
    default_code = "business_logic_error"


class VotingDeadlineExceeded(BusinessLogicError):
    """Raised when trying to change a vote after the deadline."""
    status_code = 403
    default_detail = "Votes can no longer be changed today - the deadline has passed."
    default_code = "voting_deadline_exceeded"


class MenuNotForToday(BusinessLogicError):
    """Raised when trying to vote for a menu that is not for today."""
    status_code = 400
    default_detail = "You can only vote for today's menu."
    default_code = "menu_not_for_today"


class RestaurantAlreadyExists(BusinessLogicError):
    """Raised when trying to create a restaurant with a name that already exists."""
    status_code = 400
    default_detail = "Restaurant with this name already exists."
    default_code = "restaurant_already_exists"


def api_exception_handler(exc, context):
    """Custom exception handler for consistent error responses."""
    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    payload = {
        "detail": str(detail) if detail else "Request could not be processed.",
        "errors": response.data if not detail else None,
    }
    return Response(payload, status=response.status_code, headers=response.headers)
