# Generated by Django 3.2.7 on 2022-05-13 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_remove_riderprofile_socket_security_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='riderprofile',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=1),
        ),
    ]
