# Generated by Django 3.2.7 on 2021-11-30 09:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_currentorderlocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currentorderlocation',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tracking_object', to='order.order'),
        ),
    ]
