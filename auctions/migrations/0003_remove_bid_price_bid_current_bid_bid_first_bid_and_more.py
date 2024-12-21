# Generated by Django 5.1.4 on 2024-12-21 11:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_bid_comment_listing_reply'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bid',
            name='price',
        ),
        migrations.AddField(
            model_name='bid',
            name='current_bid',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bid',
            name='first_bid',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='first_price',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='first_price', to='auctions.bid'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='current_price',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_price', to='auctions.bid'),
        ),
    ]
