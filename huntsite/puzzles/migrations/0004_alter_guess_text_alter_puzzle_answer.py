# Generated by Django 5.0.4 on 2024-07-19 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0003_alter_guess_text_alter_puzzle_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guess',
            name='text',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='answer',
            field=models.CharField(max_length=255),
        ),
    ]
