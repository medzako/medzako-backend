# Generated by Django 3.2.7 on 2022-02-07 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0020_auto_20220202_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='rider',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rider_orders', to=settings.AUTH_USER_MODEL),
        ),
    ]