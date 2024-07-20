# Generated by Django 5.0.4 on 2024-07-20 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0003_alter_guess_options_adventcalendarentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guess',
            name='is_correct',
        ),
        migrations.AddField(
            model_name='guess',
            name='evaluation',
            field=models.CharField(choices=[('correct', 'Correct'), ('incorrect', 'Incorrect'), ('already_submitted', 'Already Submitted'), ('keep_going', 'Keep Going')], default='incorrect', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='puzzle',
            name='keep_going_inputs',
            field=models.JSONField(default=list),
        ),
    ]
