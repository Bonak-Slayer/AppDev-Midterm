# Generated by Django 3.0.8 on 2021-04-07 04:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingcart', '0014_shipping_details_shipping_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shipping_details',
            name='province',
        ),
    ]