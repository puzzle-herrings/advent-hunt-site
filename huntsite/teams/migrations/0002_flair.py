# Generated by Django 5.0.4 on 2024-10-20 02:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(max_length=1023)),
                ('label', models.CharField(max_length=255)),
                ('order_by', models.IntegerField(default=0)),
                ('users', models.ManyToManyField(related_name='flairs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]