# Generated by Django 3.2.7 on 2022-06-06 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0026_pharmacyrating_riderrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='notes',
            field=models.TextField(null=True),
        ),
    ]
