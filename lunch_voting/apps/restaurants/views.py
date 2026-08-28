from rest_framework import generics, permissions

from apps.core.permissions import IsAdmin

from .models import Restaurant
from .serializers import RestaurantSerializer


class RestaurantListCreateView(generics.ListCreateAPIView):
    """List restaurants (any authenticated user) or create one (admins only).

    Read access is intentionally open to any authenticated user - employees
    need to browse restaurants too - while writes are admin-only.
    """

    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class RestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve/update/delete a single restaurant. Writes are admin-only."""

    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]
