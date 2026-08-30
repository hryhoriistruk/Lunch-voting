"""Health check endpoint for monitoring and load balancers."""
from django.db import connections
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.views import APIView

User = get_user_model()


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


class MetricsView(APIView):
    """Prometheus metrics endpoint for monitoring.

    Returns basic application metrics in Prometheus text format.
    This can be scraped by Prometheus or compatible monitoring systems.
    """

    permission_classes = []  # No authentication required for metrics

    def get(self, request, *args, **kwargs):
        """Return application metrics."""
        metrics = []

        # User counts
        total_users = User.objects.count()
        admin_users = User.objects.filter(role=User.Role.ADMIN).count()
        employee_users = User.objects.filter(role=User.Role.EMPLOYEE).count()

        metrics.append(f"# HELP lunch_voting_total_users Total number of users")
        metrics.append(f"# TYPE lunch_voting_total_users gauge")
        metrics.append(f"lunch_voting_total_users {total_users}")

        metrics.append(f"# HELP lunch_voting_admin_users Number of admin users")
        metrics.append(f"# TYPE lunch_voting_admin_users gauge")
        metrics.append(f"lunch_voting_admin_users {admin_users}")

        metrics.append(f"# HELP lunch_voting_employee_users Number of employee users")
        metrics.append(f"# TYPE lunch_voting_employee_users gauge")
        metrics.append(f"lunch_voting_employee_users {employee_users}")

        # Database status
        metrics.append(f"# HELP lunch_voting_database_status Database connectivity status (1=ok, 0=error)")
        metrics.append(f"# TYPE lunch_voting_database_status gauge")
        try:
            connections["default"].cursor()
            metrics.append(f"lunch_voting_database_status 1")
        except Exception:
            metrics.append(f"lunch_voting_database_status 0")

        # Application info
        metrics.append(f"# HELP lunch_voting_up Application uptime indicator")
        metrics.append(f"# TYPE lunch_voting_up gauge")
        metrics.append(f"lunch_voting_up 1")

        return JsonResponse({"metrics": "\n".join(metrics)}, content_type="text/plain")
