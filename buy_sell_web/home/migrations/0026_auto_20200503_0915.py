# Generated by Django 3.0.5 on 2020-05-03 09:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0025_auto_20200503_0909'),
    ]

    operations = [
        migrations.RunSQL('ALTER TABLE auth_user AUTO_INCREMENT = 1000005080;')
    ]
