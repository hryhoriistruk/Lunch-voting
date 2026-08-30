from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.views import HealthCheckView, MetricsView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Health check (no auth required)
    path("health/", HealthCheckView.as_view(), name="health-check"),
    # Metrics endpoint (no auth required)
    path("metrics/", MetricsView.as_view(), name="metrics"),
    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API v1 endpoints
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Domain APIs (v1)
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.restaurants.urls")),
    path("api/v1/", include("apps.menus.urls")),
    path("api/v1/", include("apps.votes.urls")),
]
