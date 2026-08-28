from django.urls import path

from .views import CastVoteView, TodayResultsView

urlpatterns = [
    path("votes/", CastVoteView.as_view(), name="vote-cast"),
    path("votes/results/today/", TodayResultsView.as_view(), name="vote-results-today"),
]
