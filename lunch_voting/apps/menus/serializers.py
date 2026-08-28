from rest_framework import serializers

from apps.restaurants.models import Restaurant

from .models import Menu, MenuItem


class MenuItemInputSerializer(serializers.ModelSerializer):
    """Used when an admin uploads a menu - no ``menu`` field, it's set by the view."""

    class Meta:
        model = MenuItem
        fields = ("name", "price")


class MenuUploadSerializer(serializers.ModelSerializer):
    """Creates (or replaces) a restaurant's menu for a given day, with items.

    Uploading a menu for a date that already has one replaces its items,
    so restaurants can safely re-upload corrections without creating
    duplicate menus for the same day.
    """

    items = MenuItemInputSerializer(many=True)

    class Meta:
        model = Menu
        fields = ("id", "date", "items")
        read_only_fields = ("id",)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("A menu must contain at least one item.")
        return items

    def create(self, validated_data):
        restaurant: Restaurant = self.context["restaurant"]
        items_data = validated_data.pop("items")
        menu, _created = Menu.objects.update_or_create(
            restaurant=restaurant, date=validated_data["date"], defaults={}
        )
        # Replace existing items so re-uploads don't leave stale dishes behind.
        menu.items.all().delete()
        MenuItem.objects.bulk_create(MenuItem(menu=menu, **item) for item in items_data)
        return menu


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("id", "name", "price")


class MenuSerializer(serializers.ModelSerializer):
    """Current (>= APP_VERSION_BREAKPOINT) response shape: menus grouped by restaurant."""

    restaurant_id = serializers.IntegerField(source="restaurant.id")
    restaurant_name = serializers.CharField(source="restaurant.name")
    items = MenuItemSerializer(many=True)

    class Meta:
        model = Menu
        fields = ("id", "date", "restaurant_id", "restaurant_name", "items")


class LegacyMenuItemSerializer(serializers.Serializer):
    """Legacy (< APP_VERSION_BREAKPOINT) response shape: a flat list of items.

    Older app builds expect one flat array of dishes, each carrying its own
    restaurant name/id inline, rather than menus nested per restaurant.
    """

    menu_item_id = serializers.IntegerField(source="id")
    dish = serializers.CharField(source="name")
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    restaurant_id = serializers.IntegerField(source="menu.restaurant.id")
    restaurant = serializers.CharField(source="menu.restaurant.name")
