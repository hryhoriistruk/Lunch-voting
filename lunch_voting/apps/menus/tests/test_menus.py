import pytest
from django.urls import reverse
from django.utils import timezone

from apps.menus.models import Menu

pytestmark = pytest.mark.django_db


def _menu_upload_url(restaurant_id):
    return reverse("menu-upload", kwargs={"restaurant_id": restaurant_id})


def test_admin_can_upload_todays_menu(admin_client, restaurant):
    payload = {
        "date": str(timezone.localdate()),
        "items": [
            {"name": "Tomato soup", "price": "3.00"},
            {"name": "Steak", "price": "12.50"},
        ],
    }

    response = admin_client.post(_menu_upload_url(restaurant.id), payload, format="json")

    assert response.status_code == 201
    menu = Menu.objects.get(restaurant=restaurant, date=timezone.localdate())
    assert menu.items.count() == 2


def test_employee_cannot_upload_menu(employee_client, restaurant):
    payload = {"date": str(timezone.localdate()), "items": [{"name": "Soup", "price": "3.00"}]}

    response = employee_client.post(_menu_upload_url(restaurant.id), payload, format="json")

    assert response.status_code == 403


def test_re_uploading_menu_replaces_items_instead_of_duplicating_menu(admin_client, restaurant):
    url = _menu_upload_url(restaurant.id)
    today = str(timezone.localdate())
    admin_client.post(
        url, {"date": today, "items": [{"name": "Soup", "price": "3.00"}]}, format="json"
    )

    response = admin_client.post(
        url, {"date": today, "items": [{"name": "Salad", "price": "4.00"}]}, format="json"
    )

    assert response.status_code == 201
    assert Menu.objects.filter(restaurant=restaurant, date=timezone.localdate()).count() == 1
    menu = Menu.objects.get(restaurant=restaurant, date=timezone.localdate())
    assert list(menu.items.values_list("name", flat=True)) == ["Salad"]


def test_current_app_gets_menus_grouped_by_restaurant(employee_client, todays_menu):
    response = employee_client.get(
        reverse("menu-today"), HTTP_X_APP_VERSION="2.1.0"
    )

    assert response.status_code == 200
    assert response.data[0]["restaurant_name"] == "Sunny Kitchen"
    assert len(response.data[0]["items"]) == 2


def test_legacy_app_gets_flat_list_of_dishes(employee_client, todays_menu):
    response = employee_client.get(
        reverse("menu-today"), HTTP_X_APP_VERSION="1.3.0"
    )

    assert response.status_code == 200
    assert len(response.data) == 2
    assert {"dish", "price", "restaurant", "restaurant_id", "menu_item_id"} <= set(
        response.data[0].keys()
    )


def test_missing_version_header_defaults_to_legacy_response(employee_client, todays_menu):
    response = employee_client.get(reverse("menu-today"))

    assert response.status_code == 200
    assert "dish" in response.data[0]
