# Generated by Django 5.1.4 on 2024-12-25 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_bid_first_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='first_bid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]