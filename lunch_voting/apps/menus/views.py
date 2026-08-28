from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.core.permissions import IsAdmin
from apps.restaurants.models import Restaurant

from .serializers import (
    LegacyMenuItemSerializer,
    MenuSerializer,
    MenuUploadSerializer,
)
from .services import get_todays_menu_items, get_todays_menus


class MenuUploadView(generics.CreateAPIView):
    """Admin-only: upload (or replace) a restaurant's menu for a given day.

    ``POST /api/restaurants/<restaurant_id>/menus/``
    """

    serializer_class = MenuUploadSerializer
    permission_classes = (IsAdmin,)

    def get_restaurant(self):
        restaurant_id = self.kwargs["restaurant_id"]
        try:
            return Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist as exc:
            raise NotFound("Restaurant not found.") from exc

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["restaurant"] = self.get_restaurant()
        return context


class TodayMenuView(generics.GenericAPIView):
    """Any authenticated employee: view every restaurant's menu for today.

    Response shape depends on the mobile app's build version (see
    ``apps.core.versioning``): legacy clients get a flat list of dishes,
    current clients get menus grouped by restaurant.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if request.version_info.is_legacy:
            items = get_todays_menu_items()
            data = LegacyMenuItemSerializer(items, many=True).data
        else:
            menus = get_todays_menus()
            data = MenuSerializer(menus, many=True).data
        return Response(data)
