from django.urls import path

from .views import EmployeeListCreateView

urlpatterns = [
    path("employees/", EmployeeListCreateView.as_view(), name="employee-list-create"),
]
