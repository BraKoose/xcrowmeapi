# Generated by Django 3.2.4 on 2021-06-18 13:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0005_alter_exchange_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchange',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exchangetransaction',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exchangetransaction',
            name='uid',
            field=models.CharField(blank=True, max_length=16, unique=True),
        ),
    ]
