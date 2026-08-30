"""Management command to seed the database with sample data for demo purposes."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.menus.models import Menu, MenuItem
from apps.restaurants.models import Restaurant

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with sample data for demo/testing"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database with sample data...")

        # Create admin user
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "role": User.Role.ADMIN,
                "is_superuser": True,
                "is_staff": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin/admin123"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists"))

        # Create employees
        employees_data = [
            {"username": "alice", "email": "alice@example.com", "password": "alice123"},
            {"username": "bob", "email": "bob@example.com", "password": "bob123"},
            {"username": "charlie", "email": "charlie@example.com", "password": "charlie123"},
        ]

        for emp_data in employees_data:
            employee, created = User.objects.get_or_create(
                username=emp_data["username"],
                defaults={
                    "email": emp_data["email"],
                    "role": User.Role.EMPLOYEE,
                },
            )
            if created:
                employee.set_password(emp_data["password"])
                employee.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Created employee: {emp_data['username']}/{emp_data['password']}")
                )
            else:
                self.stdout.write(self.style.WARNING(f"Employee {emp_data['username']} already exists"))

        # Create restaurants
        restaurants_data = [
            {"name": "Sunny Kitchen", "address": "1 Main St"},
            {"name": "Green Bowl", "address": "2 Second St"},
            {"name": "Pasta House", "address": "3 Third St"},
        ]

        restaurants = []
        for rest_data in restaurants_data:
            restaurant, created = Restaurant.objects.get_or_create(
                name=rest_data["name"],
                defaults={"address": rest_data["address"]},
            )
            restaurants.append(restaurant)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created restaurant: {rest_data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Restaurant {rest_data['name']} already exists"))

        # Create today's menus with items
        today = timezone.localdate()
        menu_items_data = [
            {
                "restaurant": restaurants[0],
                "items": [
                    {"name": "Tomato soup", "price": "3.00"},
                    {"name": "Grilled chicken", "price": "7.90"},
                    {"name": "Caesar salad", "price": "5.50"},
                ],
            },
            {
                "restaurant": restaurants[1],
                "items": [
                    {"name": "Veggie bowl", "price": "6.00"},
                    {"name": "Smoothie", "price": "4.00"},
                ],
            },
            {
                "restaurant": restaurants[2],
                "items": [
                    {"name": "Spaghetti carbonara", "price": "8.50"},
                    {"name": "Margherita pizza", "price": "9.00"},
                ],
            },
        ]

        for menu_data in menu_items_data:
            menu, created = Menu.objects.get_or_create(
                restaurant=menu_data["restaurant"],
                date=today,
            )
            if created:
                for item_data in menu_data["items"]:
                    MenuItem.objects.create(menu=menu, **item_data)
                self.stdout.write(
                    self.style.SUCCESS(f"Created menu for {menu_data['restaurant'].name} with {len(menu_data['items'])} items")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Menu for {menu_data['restaurant'].name} already exists")
                )

        self.stdout.write(self.style.SUCCESS("Database seeding completed!"))
        self.stdout.write("\nCredentials:")
        self.stdout.write("  Admin: admin / admin123")
        self.stdout.write("  Employees: alice / alice123, bob / bob123, charlie / charlie123")
