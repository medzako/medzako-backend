# Generated by Django 3.2.7 on 2022-03-16 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0016_riderprofile_socket_security_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='riderprofile',
            name='socket_security_code',
        ),
    ]