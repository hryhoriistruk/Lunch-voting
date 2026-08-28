from django.contrib import admin

from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "date")
    list_filter = ("date", "restaurant")
    inlines = (MenuItemInline,)
