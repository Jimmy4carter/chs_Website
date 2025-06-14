# Generated by Django 3.2.6 on 2022-09-08 13:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0005_subjectsallo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hostel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('Sex', models.CharField(max_length=255)),
                ('room_count', models.IntegerField(default=0)),
                ('capacity', models.IntegerField(default=0)),
                ('hparent2', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('hparent1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('hprefect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.students')),
            ],
        ),
        migrations.CreateModel(
            name='Rooms',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('capacity', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('hostels', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostel.hostel')),
                ('roomhead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.students')),
            ],
        ),
        migrations.CreateModel(
            name='Logbook',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rdate', models.CharField(max_length=255)),
                ('report', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.staff')),
                ('sessionid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.sessionyearmodel')),
            ],
        ),
        migrations.CreateModel(
            name='Allocations',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('allocator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.staff')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostel.rooms')),
                ('sessionid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.sessionyearmodel')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.students')),
            ],
        ),
    ]
