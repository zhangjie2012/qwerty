# Generated by Django 2.1.7 on 2019-03-03 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0008_auto_20190216_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='pin',
            field=models.BooleanField(default=False, help_text='push pin topic will sort at first', verbose_name='Pushpin topic'),
        ),
    ]
