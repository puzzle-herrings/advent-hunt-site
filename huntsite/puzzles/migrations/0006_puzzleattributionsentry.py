# Generated by Django 5.0.4 on 2024-10-19 16:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0005_clipboarddata_externallink'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuzzleAttributionsEntry',
            fields=[
                ('puzzle', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='attributions_entry', serialize=False, to='puzzles.puzzle')),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Puzzle Attributions',
            },
        ),
    ]