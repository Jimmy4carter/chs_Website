# Generated by Django 3.2.6 on 2024-05-09 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_alter_sitecontrols_countvalue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitecontrols',
            name='countvalue',
            field=models.IntegerField(default=0),
        ),
    ]
