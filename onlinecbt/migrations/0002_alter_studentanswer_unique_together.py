# Generated by Django 3.2.6 on 2024-12-10 14:55

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('onlinecbt', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='studentanswer',
            unique_together={('student', 'schedule', 'objective_question')},
        ),
    ]
