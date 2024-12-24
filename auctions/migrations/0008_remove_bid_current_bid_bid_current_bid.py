# Generated by Django 5.1.4 on 2024-12-24 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_remove_bid_current_bid_bid_current_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bid',
            name='current_bid',
        ),
        migrations.AddField(
            model_name='bid',
            name='current_bid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]