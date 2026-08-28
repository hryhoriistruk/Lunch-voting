"""Query helpers for menus.

Pulling these out of the view keeps ``views.py`` focused on HTTP concerns
(permissions, status codes) while the "what data do we actually need"
question lives here and can be unit-tested or reused independently.
"""
from django.utils import timezone

from .models import Menu, MenuItem


def get_todays_menus():
    """Return today's menus with restaurants and items pre-fetched.

    ``select_related``/``prefetch_related`` avoid N+1 queries when the
    serializer walks ``menu.restaurant`` and ``menu.items`` for every menu.
    """
    today = timezone.localdate()
    return (
        Menu.objects.filter(date=today)
        .select_related("restaurant")
        .prefetch_related("items")
    )


def get_todays_menu_items():
    """Return today's menu items as a flat queryset (for the legacy response)."""
    today = timezone.localdate()
    return MenuItem.objects.filter(menu__date=today).select_related("menu__restaurant")
