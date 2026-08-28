"""Health check endpoint for monitoring and load balancers."""
from django.db import connections
from django.http import JsonResponse
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Simple health check endpoint.

    Returns 200 OK if the service is healthy, including database connectivity.
    This is useful for monitoring systems, load balancers, and container orchestration.
    """

    permission_classes = []  # No authentication required for health checks

    def get(self, request, *args, **kwargs):
        """Check service health including database connectivity."""
        health_status = {"status": "healthy", "checks": {}}

        # Check database connectivity
        try:
            db_conn = connections["default"]
            db_conn.cursor()
            health_status["checks"]["database"] = "ok"
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = f"error: {str(e)}"

        status_code = 200 if health_status["status"] == "healthy" else 503
        return JsonResponse(health_status, status=status_code)
