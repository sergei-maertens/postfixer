# Generated by Django 2.2.1 on 2019-06-01 05:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mail", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="domain",
            name="active",
            field=models.BooleanField(default=True, verbose_name="active"),
        ),
        migrations.AddField(
            model_name="forward",
            name="active",
            field=models.BooleanField(default=True, verbose_name="active"),
        ),
    ]
