# Generated by Django 3.2.6 on 2022-09-13 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_subjectsallo'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessionplan',
            name='session_year',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, to='accounts.sessionyearmodel'),
            preserve_default=False,
        ),
    ]
