"""Request/response logging middleware for debugging and monitoring.

Logs HTTP requests and responses with timing information to help with
debugging and performance monitoring.
"""
import time
import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log HTTP requests and responses with timing."""

    def process_request(self, request):
        """Log incoming request and start timing."""
        request.start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
            f"User: {request.user if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'}"
        )

    def process_response(self, request, response):
        """Log response details with timing."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"Response: {response.status_code} "
                f"Duration: {duration:.3f}s "
                f"Path: {request.path}"
            )
        
        return response
