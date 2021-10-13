# Generated by Django 3.2.7 on 2021-10-02 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='scientific_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='medication',
            name='scientific_name',
            field=models.CharField(default='frer', max_length=50),
            preserve_default=False,
        ),
    ]
