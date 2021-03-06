# Generated by Django 2.0.4 on 2018-06-04 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booktifier', '0011_auto_20180601_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buser',
            name='favourites',
            field=models.ManyToManyField(blank=True, related_name='Favourites', to='booktifier.Book'),
        ),
        migrations.AlterField(
            model_name='buser',
            name='read',
            field=models.ManyToManyField(blank=True, related_name='Read', to='booktifier.Book'),
        ),
    ]
