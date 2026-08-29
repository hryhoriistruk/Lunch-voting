from django.utils import timezone
from rest_framework import serializers

from apps.menus.models import Menu

from .models import Vote


class VoteCastSerializer(serializers.ModelSerializer):
    """Input for ``POST /api/votes/`` - the employee just picks a menu."""

    menu_id = serializers.PrimaryKeyRelatedField(
        source="menu", queryset=Menu.objects.all()
    )

    class Meta:
        model = Vote
        fields = ("id", "menu_id", "date", "created_at", "updated_at")
        read_only_fields = ("id", "date", "created_at", "updated_at")

    def validate(self, data):
        """Validate that the requested menu is for today.

        Deadline handling (first vote vs. changing an existing vote) is
        business logic and lives in services.cast_vote() - not here, so
        there is exactly one place that decides whether a vote is allowed.
        """
        menu = data["menu"]
        today = timezone.localdate()
        if menu.date != today:
            raise serializers.ValidationError(
                "You can only vote for today's menu."
            )
        return data


class VoteSerializer(serializers.ModelSerializer):
    """Read-only representation of a stored vote."""

    restaurant_name = serializers.CharField(source="menu.restaurant.name", read_only=True)

    class Meta:
        model = Vote
        fields = ("id", "menu", "restaurant_name", "date", "created_at", "updated_at")


class ResultRowSerializer(serializers.Serializer):
    """Current (>= APP_VERSION_BREAKPOINT) results response shape: one row per restaurant."""

    restaurant_id = serializers.IntegerField()
    restaurant_name = serializers.CharField()
    menu_id = serializers.IntegerField()
    votes = serializers.IntegerField()


class LegacyResultRowSerializer(serializers.Serializer):
    """Legacy (< APP_VERSION_BREAKPOINT) results response shape.

    Older clients expect the winning restaurant's name under the key
    ``winner`` and the vote total under ``count`` instead of ``votes``.
    """

    winner = serializers.CharField(source="restaurant_name")
    restaurant_id = serializers.IntegerField()
    count = serializers.IntegerField(source="votes")
