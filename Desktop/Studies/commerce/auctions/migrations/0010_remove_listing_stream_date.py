# Generated by Django 3.0.8 on 2021-05-10 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20210511_0441'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='stream_date',
        ),
    ]
