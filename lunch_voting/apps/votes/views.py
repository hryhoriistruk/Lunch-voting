from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsEmployee

from .serializers import (
    LegacyResultRowSerializer,
    ResultRowSerializer,
    VoteCastSerializer,
)
from .services import cast_vote, get_todays_results


class CastVoteView(generics.GenericAPIView):
    """Employee-only: cast (or change, before the deadline) today's vote.

    ``POST /api/votes/`` with body ``{"menu_id": <id>}``.
    """

    serializer_class = VoteCastSerializer
    permission_classes = (IsEmployee,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = cast_vote(employee=request.user, menu=serializer.validated_data["menu"])
        return Response(self.get_serializer(vote).data, status=status.HTTP_200_OK)


class TodayResultsView(APIView):
    """Any authenticated user: current standings for today's vote.

    Response shape depends on the mobile app's build version, matching the
    same legacy/current split used by ``TodayMenuView``.
    """

    def get(self, request, *args, **kwargs):
        results = get_todays_results()
        if request.version_info.is_legacy:
            data = LegacyResultRowSerializer(results, many=True).data
        else:
            data = ResultRowSerializer(results, many=True).data
        return Response(data)
