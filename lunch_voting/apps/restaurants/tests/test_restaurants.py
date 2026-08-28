import pytest
from django.urls import reverse

from apps.restaurants.models import Restaurant

pytestmark = pytest.mark.django_db


def test_admin_can_create_restaurant(admin_client):
    response = admin_client.post(
        reverse("restaurant-list-create"), {"name": "Pasta House", "address": "9 Food St"}
    )

    assert response.status_code == 201
    assert Restaurant.objects.filter(name="Pasta House").exists()


def test_employee_cannot_create_restaurant(employee_client):
    response = employee_client.post(reverse("restaurant-list-create"), {"name": "No Access"})

    assert response.status_code == 403
    assert not Restaurant.objects.filter(name="No Access").exists()


def test_employee_can_list_restaurants(employee_client, restaurant):
    response = employee_client.get(reverse("restaurant-list-create"))

    assert response.status_code == 200
    names = [row["name"] for row in response.data["results"]]
    assert "Sunny Kitchen" in names


def test_restaurant_name_must_be_unique(admin_client, restaurant):
    response = admin_client.post(reverse("restaurant-list-create"), {"name": restaurant.name})

    assert response.status_code == 400


def test_admin_can_update_restaurant(admin_client, restaurant):
    response = admin_client.put(
        reverse("restaurant-detail", kwargs={"pk": restaurant.id}),
        {"name": "Updated Name", "address": "New Address"},
    )

    assert response.status_code == 200
    restaurant.refresh_from_db()
    assert restaurant.name == "Updated Name"
    assert restaurant.address == "New Address"


def test_employee_cannot_update_restaurant(employee_client, restaurant):
    response = employee_client.put(
        reverse("restaurant-detail", kwargs={"pk": restaurant.id}),
        {"name": "Hacked Name", "address": "Hacked Address"},
    )

    assert response.status_code == 403
    restaurant.refresh_from_db()
    assert restaurant.name != "Hacked Name"


def test_admin_can_delete_restaurant(admin_client, restaurant):
    response = admin_client.delete(reverse("restaurant-detail", kwargs={"pk": restaurant.id}))

    assert response.status_code == 204
    assert not Restaurant.objects.filter(id=restaurant.id).exists()


def test_employee_cannot_delete_restaurant(employee_client, restaurant):
    response = employee_client.delete(reverse("restaurant-detail", kwargs={"pk": restaurant.id}))

    assert response.status_code == 403
    assert Restaurant.objects.filter(id=restaurant.id).exists()


def test_restaurants_are_ordered_by_name(admin_client, restaurant, another_restaurant):
    response = admin_client.get(reverse("restaurant-list-create"))

    assert response.status_code == 200
    names = [row["name"] for row in response.data["results"]]
    assert names == sorted(names)
