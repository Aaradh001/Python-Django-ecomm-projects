# Generated by Django 4.2.3 on 2023-10-06 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet_management', '0002_wallet_is_used'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wallet',
            name='is_used',
        ),
    ]
