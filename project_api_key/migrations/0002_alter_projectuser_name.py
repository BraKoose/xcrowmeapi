# Generated by Django 3.2.4 on 2021-06-16 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_api_key', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectuser',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
