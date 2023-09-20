# Generated by Django 4.2.3 on 2023-09-17 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_alter_order_order_total_alter_order_tax_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Order placed', 'Order placed'), ('Accepted', 'Accepted'), ('Delivered', 'Delivered'), ('Cancelled by Admin', 'Cancelled Admin'), ('Cancelled by User', 'Cancelled User'), ('Returned', 'Returned')], default='New', max_length=20),
        ),
    ]
