# Generated by Django 5.0.4 on 2024-05-11 18:57

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solve',
            old_name='solved_datetime',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='guess',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
