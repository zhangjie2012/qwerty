# Generated by Django 2.1.3 on 2018-12-09 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='education',
            options={'ordering': ['start_dt'], 'verbose_name': 'Education', 'verbose_name_plural': 'Educations'},
        ),
        migrations.AlterModelOptions(
            name='job',
            options={'ordering': ['-start_dt'], 'verbose_name': 'job', 'verbose_name_plural': 'jobs'},
        ),
    ]