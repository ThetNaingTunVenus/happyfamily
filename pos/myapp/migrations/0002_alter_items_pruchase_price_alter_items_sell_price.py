# Generated by Django 5.0.3 on 2024-03-11 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='items',
            name='pruchase_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='items',
            name='sell_price',
            field=models.IntegerField(default=0),
        ),
    ]
