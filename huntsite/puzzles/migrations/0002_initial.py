# Generated by Django 5.0.4 on 2024-08-25 22:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('puzzles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='finish',
            name='user',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='guess',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='metapuzzleinfo',
            name='puzzle',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='meta_info', to='puzzles.puzzle'),
        ),
        migrations.AddField(
            model_name='guess',
            name='puzzle',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='puzzles.puzzle'),
        ),
        migrations.AddField(
            model_name='erratum',
            name='puzzle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='errata', to='puzzles.puzzle'),
        ),
        migrations.AddField(
            model_name='adventcalendarentry',
            name='puzzle',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='calendar_entry', to='puzzles.puzzle'),
        ),
        migrations.AddField(
            model_name='solve',
            name='puzzle',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='puzzles.puzzle'),
        ),
        migrations.AddField(
            model_name='solve',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='solve',
            unique_together={('user', 'puzzle')},
        ),
    ]
