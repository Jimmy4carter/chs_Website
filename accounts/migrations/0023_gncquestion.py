# Generated by Django 3.2.6 on 2024-05-22 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_alter_entryattestation_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='GncQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('field_type', models.CharField(choices=[('text', 'Text'), ('radio', 'Radio'), ('checkbox', 'Checkbox'), ('select', 'Select')], max_length=100)),
                ('form_type', models.CharField(choices=[('single', 'Single'), ('multiple', 'Multiple')], max_length=100)),
            ],
        ),
    ]
