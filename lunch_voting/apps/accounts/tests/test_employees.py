import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_admin_can_create_employee(admin_client):
    payload = {"username": "charlie", "email": "charlie@example.com", "password": "charlie-pass123"}

    response = admin_client.post(reverse("employee-list-create"), payload)

    assert response.status_code == 201
    created = User.objects.get(username="charlie")
    assert created.role == User.Role.EMPLOYEE
    # password must never be returned or stored in plain text
    assert "password" not in response.data
    assert created.check_password("charlie-pass123")


def test_employee_cannot_create_another_employee(employee_client):
    payload = {"username": "dave", "email": "dave@example.com", "password": "dave-pass123"}

    response = employee_client.post(reverse("employee-list-create"), payload)

    assert response.status_code == 403


def test_created_employee_role_cannot_be_overridden_by_client(admin_client):
    payload = {
        "username": "eve",
        "email": "eve@example.com",
        "password": "eve-pass123",
        "role": "ADMIN",  # attempted privilege escalation, should be ignored
    }

    response = admin_client.post(reverse("employee-list-create"), payload)

    assert response.status_code == 201
    assert User.objects.get(username="eve").role == User.Role.EMPLOYEE
