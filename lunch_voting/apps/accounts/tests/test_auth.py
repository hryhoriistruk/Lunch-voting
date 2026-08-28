import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_employee_can_obtain_jwt_token_with_valid_credentials(api_client, employee_user):
    response = api_client.post(
        reverse("token_obtain_pair"),
        {"username": "alice", "password": "alice-pass123"},
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


def test_token_request_with_wrong_password_is_rejected(api_client, employee_user):
    response = api_client.post(
        reverse("token_obtain_pair"),
        {"username": "alice", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_endpoints_require_authentication(api_client):
    response = api_client.get(reverse("restaurant-list-create"))

    assert response.status_code == 401
