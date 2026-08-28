from django.db import models


class Restaurant(models.Model):
    """A restaurant that can publish a daily lunch menu."""

    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name
