# Generated by Django 3.0.8 on 2021-04-07 04:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingcart', '0013_shipping_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipping_details',
            name='shipping_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipping_reference', to='shoppingcart.Shipping'),
        ),
    ]
