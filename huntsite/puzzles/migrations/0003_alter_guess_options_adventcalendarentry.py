# Generated by Django 5.0.4 on 2024-07-19 20:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='guess',
            options={'verbose_name_plural': 'Guesses'},
        ),
        migrations.CreateModel(
            name='AdventCalendarEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(default=-1)),
                ('puzzle', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='calendar_entry', to='puzzles.puzzle')),
            ],
            options={
                'verbose_name_plural': 'Advent Calendar Entries',
                'ordering': ['day'],
            },
        ),
    ]
