# Generated by Django 5.0.4 on 2024-07-29 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='storyentry',
            name='is_final',
            field=models.BooleanField(default=False),
        ),
    ]