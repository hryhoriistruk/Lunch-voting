"""Shared pytest fixtures.

Keeping fixtures at the repo root makes them available to every app's test
package without imports, which is the standard pytest-django convention.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.menus.models import Menu, MenuItem
from apps.restaurants.models import Restaurant

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin", password="admin-pass123", role=User.Role.ADMIN
    )


@pytest.fixture
def employee_user(db):
    return User.objects.create_user(
        username="alice", password="alice-pass123", role=User.Role.EMPLOYEE
    )


@pytest.fixture
def another_employee_user(db):
    return User.objects.create_user(
        username="bob", password="bob-pass123", role=User.Role.EMPLOYEE
    )


def _authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    return _authenticated_client(admin_user)


@pytest.fixture
def employee_client(employee_user):
    return _authenticated_client(employee_user)


@pytest.fixture
def restaurant(db):
    return Restaurant.objects.create(name="Sunny Kitchen", address="1 Main St")


@pytest.fixture
def another_restaurant(db):
    return Restaurant.objects.create(name="Green Bowl", address="2 Second St")


@pytest.fixture
def todays_menu(restaurant):
    menu = Menu.objects.create(restaurant=restaurant, date=timezone.localdate())
    MenuItem.objects.create(menu=menu, name="Soup of the day", price="3.50")
    MenuItem.objects.create(menu=menu, name="Grilled chicken", price="7.90")
    return menu


@pytest.fixture
def another_todays_menu(another_restaurant):
    menu = Menu.objects.create(restaurant=another_restaurant, date=timezone.localdate())
    MenuItem.objects.create(menu=menu, name="Veggie bowl", price="6.00")
    return menu
