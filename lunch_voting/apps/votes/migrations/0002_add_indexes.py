# Generated migration for database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("votes", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="vote",
            index=models.Index(fields=["date"], name="votes_date_idx"),
        ),
        migrations.AddIndex(
            model_name="vote",
            index=models.Index(fields=["employee", "date"], name="votes_employee_date_idx"),
        ),
        migrations.AddIndex(
            model_name="vote",
            index=models.Index(fields=["menu", "date"], name="votes_menu_date_idx"),
        ),
    ]
