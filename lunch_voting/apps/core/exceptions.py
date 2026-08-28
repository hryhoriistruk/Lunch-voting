"""A single, predictable error response shape for the whole API.

Without this, DRF's default handler returns different payload shapes for
validation errors, permission errors, etc. Front-end/mobile clients
benefit from always seeing ``{"detail": ..., "errors": {...}}``.
"""
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    payload = {
        "detail": str(detail) if detail else "Request could not be processed.",
        "errors": response.data if not detail else None,
    }
    return Response(payload, status=response.status_code, headers=response.headers)
