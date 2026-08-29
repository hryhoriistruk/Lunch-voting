import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.menus.models import Menu, MenuItem
from apps.votes.models import Vote

pytestmark = pytest.mark.django_db

VOTES_URL = reverse("vote-cast")
RESULTS_URL = reverse("vote-results-today")


def test_employee_can_cast_a_vote(employee_client, employee_user, todays_menu):
    response = employee_client.post(VOTES_URL, {"menu_id": todays_menu.id})

    assert response.status_code == 200
    assert Vote.objects.filter(employee=employee_user, menu=todays_menu).exists()


def test_admin_cannot_cast_a_vote(admin_client, todays_menu):
    response = admin_client.post(VOTES_URL, {"menu_id": todays_menu.id})

    assert response.status_code == 403


def test_cannot_vote_for_a_menu_that_is_not_todays(employee_client, restaurant):
    yesterday_menu = Menu.objects.create(
        restaurant=restaurant, date=timezone.localdate() - datetime.timedelta(days=1)
    )
    MenuItem.objects.create(menu=yesterday_menu, name="Old dish", price="1.00")

    response = employee_client.post(VOTES_URL, {"menu_id": yesterday_menu.id})

    assert response.status_code == 400


def test_employee_can_change_vote_before_deadline(
    employee_client, employee_user, todays_menu, another_todays_menu, monkeypatch
):
    monkeypatch.setattr("apps.votes.services._voting_deadline_passed", lambda: False)
    employee_client.post(VOTES_URL, {"menu_id": todays_menu.id})

    response = employee_client.post(VOTES_URL, {"menu_id": another_todays_menu.id})

    assert response.status_code == 200
    assert Vote.objects.filter(employee=employee_user).count() == 1
    assert Vote.objects.get(employee=employee_user).menu_id == another_todays_menu.id


def test_employee_cannot_change_vote_after_deadline(
    employee_client, todays_menu, another_todays_menu, monkeypatch
):
    monkeypatch.setattr("apps.votes.services._voting_deadline_passed", lambda: False)
    employee_client.post(VOTES_URL, {"menu_id": todays_menu.id})

    monkeypatch.setattr("apps.votes.services._voting_deadline_passed", lambda: True)
    response = employee_client.post(VOTES_URL, {"menu_id": another_todays_menu.id})

    assert response.status_code == 403
    assert Vote.objects.get().menu_id == todays_menu.id


def test_results_current_format_includes_zero_vote_restaurants(
    employee_client, todays_menu, another_todays_menu, employee_user
):
    Vote.objects.create(employee=employee_user, menu=todays_menu, date=timezone.localdate())

    response = employee_client.get(RESULTS_URL, HTTP_X_APP_VERSION="2.0.0")

    assert response.status_code == 200
    by_restaurant = {row["restaurant_id"]: row["votes"] for row in response.data}
    assert by_restaurant[todays_menu.restaurant_id] == 1
    assert by_restaurant[another_todays_menu.restaurant_id] == 0


def test_results_legacy_format_uses_winner_and_count_keys(
    employee_client, todays_menu, employee_user
):
    Vote.objects.create(employee=employee_user, menu=todays_menu, date=timezone.localdate())

    response = employee_client.get(RESULTS_URL, HTTP_X_APP_VERSION="1.0.0")

    assert response.status_code == 200
    top_row = response.data[0]
    assert top_row["winner"] == "Sunny Kitchen"
    assert top_row["count"] == 1


def test_results_are_ordered_by_vote_count_descending(
    employee_client, another_employee_user, employee_user, todays_menu, another_todays_menu
):
    Vote.objects.create(employee=employee_user, menu=another_todays_menu, date=timezone.localdate())
    Vote.objects.create(
        employee=another_employee_user, menu=another_todays_menu, date=timezone.localdate()
    )

    response = employee_client.get(RESULTS_URL, HTTP_X_APP_VERSION="2.0.0")

    assert response.data[0]["restaurant_id"] == another_todays_menu.restaurant_id
    assert response.data[0]["votes"] == 2


def test_employee_can_cast_first_vote_even_after_deadline(
    api_client, employee_user, todays_menu, monkeypatch
):
    """A employee who hasn't voted yet today can still vote after the
    deadline hour - the deadline only blocks *changing* an existing vote.
    """
    monkeypatch.setattr("apps.votes.services._voting_deadline_passed", lambda: True)

    api_client.force_authenticate(user=employee_user)
    response = api_client.post("/api/votes/", {"menu_id": todays_menu.id})

    assert response.status_code == 200
    assert response.data["menu_id"] == todays_menu.id
