# Generated by Django 3.0.8 on 2021-06-02 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_auto_20210601_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='value',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
