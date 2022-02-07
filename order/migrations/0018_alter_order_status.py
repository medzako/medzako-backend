# Generated by Django 3.2.7 on 2022-01-31 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_auto_20220131_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('received', 'received'), ('accepted', 'accepted'), ('dispatched', 'dispatched'), ('delivered', 'delivered'), ('canceled', 'canceled'), ('rejected', 'rejected')], default='Received', max_length=30),
        ),
    ]