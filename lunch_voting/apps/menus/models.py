from django.db import models
from django.utils import timezone


class Menu(models.Model):
    """A restaurant's menu for one specific day.

    A restaurant can only have a single menu per day (enforced by the
    unique_together constraint below), matching the "menu for each day"
    requirement.
    """

    restaurant = models.ForeignKey(
        "restaurants.Restaurant", on_delete=models.CASCADE, related_name="menus"
    )
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("restaurant", "date"), name="one_menu_per_restaurant_per_day"
            )
        ]
        ordering = ("-date",)
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["restaurant", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.restaurant.name} - {self.date}"


class MenuItem(models.Model):
    """A single dish on a menu."""

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.name} ({self.price})"
