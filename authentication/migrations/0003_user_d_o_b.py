# Generated by Django 3.2.7 on 2021-10-25 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='d_o_b',
            field=models.DateField(default='2000-8-8'),
            preserve_default=False,
        ),
    ]
