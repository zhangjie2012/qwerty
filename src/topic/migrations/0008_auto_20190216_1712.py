# Generated by Django 2.1.7 on 2019-02-16 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0007_auto_20190216_1711'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ('archive', '-pin', 'title'), 'verbose_name': 'Topic', 'verbose_name_plural': 'Topics'},
        ),
    ]
