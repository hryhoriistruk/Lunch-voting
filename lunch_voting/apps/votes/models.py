from django.conf import settings
from django.db import models
from django.utils import timezone


class Vote(models.Model):
    """One employee's lunch vote for one day.

    ``date`` is denormalized from ``menu.date`` so we can enforce "one vote
    per employee per day" with a simple database constraint instead of a
    cross-table lookup, and so results queries don't need to join through
    menu at all.
    """

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    menu = models.ForeignKey("menus.Menu", on_delete=models.CASCADE, related_name="votes")
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("employee", "date"), name="one_vote_per_employee_per_day"
            )
        ]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["employee", "date"]),
            models.Index(fields=["menu", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.employee.username} -> {self.menu.restaurant.name} ({self.date})"
