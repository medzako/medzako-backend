# Generated by Django 3.2.7 on 2021-10-28 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_auto_20211027_1059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='image',
            new_name='prescription',
        ),
    ]