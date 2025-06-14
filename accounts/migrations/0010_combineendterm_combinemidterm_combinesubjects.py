# Generated by Django 3.2.6 on 2023-06-05 09:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_lessionplan_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='CombineSubjects',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('subject_main', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.subjects')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CombineMidTerm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('resumption_text', models.FloatField(default=0)),
                ('class_work', models.FloatField(default=0)),
                ('assignment', models.FloatField(default=0)),
                ('midterm_exam', models.FloatField(default=0)),
                ('total_score', models.FloatField(default=0)),
                ('grades', models.CharField(default='F', max_length=20)),
                ('remark', models.CharField(default='Poor', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('session_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.sessionyearmodel')),
                ('students_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.students')),
                ('subjects_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.combinesubjects')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.terms')),
            ],
        ),
        migrations.CreateModel(
            name='CombineEndTerm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ca1', models.FloatField(default=0)),
                ('ca2', models.FloatField(default=0)),
                ('project_practical', models.FloatField(default=0)),
                ('class_work', models.FloatField(default=0)),
                ('sec_total', models.FloatField(default=0)),
                ('first_total', models.FloatField(default=0)),
                ('second_total', models.FloatField(default=0)),
                ('endterm_exam', models.FloatField(default=0)),
                ('total', models.FloatField(default=0)),
                ('grades', models.CharField(default='F', max_length=20)),
                ('effort', models.CharField(default='00', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('session_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.sessionyearmodel')),
                ('students_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.students')),
                ('subjects_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.combinesubjects')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.terms')),
            ],
        ),
    ]
