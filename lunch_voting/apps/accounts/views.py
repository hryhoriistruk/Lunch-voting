from django.contrib.auth import get_user_model
from rest_framework import generics

from apps.core.permissions import IsAdmin

from .serializers import EmployeeCreateSerializer, EmployeeSerializer

User = get_user_model()


class EmployeeListCreateView(generics.ListCreateAPIView):
    """Admin-only endpoint to list existing employees and create new ones."""

    queryset = User.objects.filter(role=User.Role.EMPLOYEE).order_by("username")
    permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        return EmployeeCreateSerializer if self.request.method == "POST" else EmployeeSerializer
