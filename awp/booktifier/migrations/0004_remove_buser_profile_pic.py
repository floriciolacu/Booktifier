# Generated by Django 2.0.2 on 2018-03-22 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booktifier', '0003_book_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buser',
            name='profile_pic',
        ),
    ]
