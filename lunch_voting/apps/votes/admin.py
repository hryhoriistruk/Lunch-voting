from django.contrib import admin

from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("employee", "menu", "date", "created_at")
    list_filter = ("date",)
