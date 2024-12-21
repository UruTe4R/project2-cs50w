# Generated by Django 5.1.4 on 2024-12-21 12:19

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_listing_current_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='creation_date',
            new_name='bid_date',
        ),
        migrations.RemoveField(
            model_name='bid',
            name='seller',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='current_price',
        ),
        migrations.AddField(
            model_name='bid',
            name='target_listing',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='target', to='auctions.listing'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='owner',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='first_price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
