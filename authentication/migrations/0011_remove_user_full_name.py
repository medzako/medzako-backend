# Generated by Django 3.2.7 on 2022-02-07 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_auto_20220207_2135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='full_name',
        ),
    ]
