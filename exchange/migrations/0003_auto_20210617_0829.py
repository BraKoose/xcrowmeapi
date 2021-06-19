# Generated by Django 3.2.4 on 2021-06-17 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0002_alter_currency_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='value',
            field=models.FloatField(default=0.0, verbose_name='Value per dollar'),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='exchange_address',
            field=models.TextField(blank=True),
        ),
    ]
