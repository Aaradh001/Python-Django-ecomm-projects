# Generated by Django 4.2.3 on 2023-09-13 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_order_wallet_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_total',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.DecimalField(decimal_places=2, max_digits=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='wallet_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50, null=True),
        ),
    ]
