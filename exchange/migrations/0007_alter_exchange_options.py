# Generated by Django 3.2.4 on 2021-06-18 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0006_auto_20210618_1412'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exchange',
            options={'ordering': ['created']},
        ),
    ]
