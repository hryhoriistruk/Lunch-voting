"""Query helpers for menus.

Pulling these out of the view keeps ``views.py`` focused on HTTP concerns
(permissions, status codes) while the "what data do we actually need"
question lives here and can be unit-tested or reused independently.
"""
from django.core.cache import cache
from django.utils import timezone

from .models import Menu, MenuItem


def get_todays_menus():
    """Return today's menus with restaurants and items pre-fetched.

    ``select_related``/``prefetch_related`` avoid N+1 queries when the
    serializer walks ``menu.restaurant`` and ``menu.items`` for every menu.
    Results are cached for 15 minutes.
    """
    today = timezone.localdate()
    cache_key = f"todays_menus_{today}"

    menus = cache.get(cache_key)
    if menus is None:
        menus = (
            Menu.objects.filter(date=today)
            .select_related("restaurant")
            .prefetch_related("items")
        )
        cache.set(cache_key, menus, 60 * 15)  # Cache for 15 minutes

    return menus


def get_todays_menu_items():
    """Return today's menu items as a flat queryset (for the legacy response).

    Results are cached for 15 minutes.
    """
    today = timezone.localdate()
    cache_key = f"todays_menu_items_{today}"

    items = cache.get(cache_key)
    if items is None:
        items = MenuItem.objects.filter(menu__date=today).select_related("menu__restaurant")
        cache.set(cache_key, items, 60 * 15)  # Cache for 15 minutes

    return items
