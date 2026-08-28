# Generated migration for database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menus", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="menu",
            index=models.Index(fields=["date"], name="menus_date_idx"),
        ),
        migrations.AddIndex(
            model_name="menu",
            index=models.Index(fields=["restaurant", "date"], name="menus_restaurant_date_idx"),
        ),
    ]
