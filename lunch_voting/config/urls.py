from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Health check (no auth required)
    path("health/", HealthCheckView.as_view(), name="health-check"),
    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Authentication (JWT)
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Domain APIs
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.restaurants.urls")),
    path("api/", include("apps.menus.urls")),
    path("api/", include("apps.votes.urls")),
]
