# Generated by Django 5.0.4 on 2024-08-03 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_finished',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]