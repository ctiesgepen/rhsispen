# Generated by Django 3.2 on 2021-07-06 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('namp', '0002_auto_20210706_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='periodoacao',
            name='data_final',
            field=models.DateTimeField(),
        ),
    ]
