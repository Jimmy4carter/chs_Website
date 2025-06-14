# Generated by Django 3.2.6 on 2024-05-22 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_gncquestion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gncquestion',
            name='field_type',
            field=models.CharField(choices=[('Science', 'Science'), ('Humanities', 'Humanities'), ('Business', 'Business'), ('Technology', 'Technology')], max_length=100),
        ),
        migrations.AlterField(
            model_name='gncquestion',
            name='form_type',
            field=models.CharField(choices=[('A', 'Form A'), ('B', 'Form B'), ('C', 'Form C'), ('D', 'Form D'), ('E', 'Form E'), ('F', 'Form F'), ('G', 'Form G'), ('H', 'Form H'), ('I', 'Form I'), ('J', 'Form J'), ('K', 'Form K'), ('L', 'Form L'), ('M', 'Form M'), ('N', 'Form N'), ('O', 'Form O'), ('P', 'Form P'), ('Q', 'Form Q'), ('R', 'Form R'), ('S', 'Form S')], max_length=100),
        ),
    ]
