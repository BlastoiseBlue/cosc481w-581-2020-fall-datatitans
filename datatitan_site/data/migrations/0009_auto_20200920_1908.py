# Generated by Django 3.1.1 on 2020-09-20 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_coviddataraw_new_tests_smoothed_per_thousand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coviddataraw',
            name='new_tests',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
