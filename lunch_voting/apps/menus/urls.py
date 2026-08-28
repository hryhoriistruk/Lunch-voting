from django.urls import path

from .views import MenuUploadView, TodayMenuView

urlpatterns = [
    path("restaurants/<int:restaurant_id>/menus/", MenuUploadView.as_view(), name="menu-upload"),
    path("menus/today/", TodayMenuView.as_view(), name="menu-today"),
]
