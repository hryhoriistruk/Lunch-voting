"""Business logic for casting votes and computing results.

Isolating this from the view/serializer layer means the "can this vote be
changed right now?" rule is defined and tested in exactly one place.
"""
from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from apps.menus.models import Menu
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Vote


class VoteChangeNotAllowed(PermissionDenied):
    default_detail = "Votes can no longer be changed today - the deadline has passed."


def _voting_deadline_passed() -> bool:
    """Whether the daily vote-change cut-off (settings.VOTE_DEADLINE_HOUR) has passed."""
    return timezone.localtime().hour >= settings.VOTE_DEADLINE_HOUR


def cast_vote(employee, menu: Menu) -> Vote:
    """Register (or update) an employee's vote for today.

    Rules:
      * An employee can only vote for a menu published for *today*.
      * An employee may change their mind and vote again the same day,
        but only before the configured deadline hour.
    """
    today = timezone.localdate()
    if menu.date != today:
        raise ValidationError("You can only vote for today's menu.")

    existing_vote = Vote.objects.filter(employee=employee, date=today).first()
    if existing_vote is None:
        return Vote.objects.create(employee=employee, menu=menu, date=today)

    if _voting_deadline_passed():
        raise VoteChangeNotAllowed()

    existing_vote.menu = menu
    existing_vote.save(update_fields=("menu", "updated_at"))
    return existing_vote


def get_todays_results():
    """Aggregate today's votes per restaurant, ordered by popularity.

    Returns a list of dicts: restaurant id/name, menu id and vote count,
    including restaurants that received zero votes today (so clients don't
    need a separate call to know which restaurants published a menu).
    """
    today = timezone.localdate()
    menus = Menu.objects.filter(date=today).select_related("restaurant")

    vote_counts = dict(
        Vote.objects.filter(date=today)
        .values("menu_id")
        .annotate(count=Count("id"))
        .values_list("menu_id", "count")
    )

    results = [
        {
            "menu_id": menu.id,
            "restaurant_id": menu.restaurant.id,
            "restaurant_name": menu.restaurant.name,
            "votes": vote_counts.get(menu.id, 0),
        }
        for menu in menus
    ]
    results.sort(key=lambda row: row["votes"], reverse=True)
    return results
