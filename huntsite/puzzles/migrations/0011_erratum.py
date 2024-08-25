# Generated by Django 5.0.4 on 2024-08-25 01:50

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0010_alter_metapuzzleinfo_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Erratum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('puzzle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='puzzles.puzzle')),
            ],
            options={
                'verbose_name_plural': 'Errata',
            },
        ),
    ]
