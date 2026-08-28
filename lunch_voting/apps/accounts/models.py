from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A single user model shared by admins and employees.

    Using one model with a ``role`` field (instead of two separate models)
    keeps authentication simple - everyone logs in the same way - while
    ``is_admin`` / ``is_employee`` helpers keep the call sites readable.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EMPLOYEE = "EMPLOYEE", "Employee"

    role = models.CharField(max_length=16, choices=Role.choices, default=Role.EMPLOYEE)

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_employee(self) -> bool:
        return self.role == self.Role.EMPLOYEE

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
