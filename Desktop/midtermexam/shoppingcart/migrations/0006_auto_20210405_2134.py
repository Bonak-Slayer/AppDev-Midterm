# Generated by Django 3.0.8 on 2021-04-05 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingcart', '0005_auto_20210405_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart_item',
            name='cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='corresponding_cart', to='shoppingcart.Cart'),
        ),
    ]