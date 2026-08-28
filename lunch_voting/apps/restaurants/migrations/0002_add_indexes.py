# Generated migration for database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("restaurants", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="restaurant",
            index=models.Index(fields=["name"], name="restaurants_name_idx"),
        ),
    ]
