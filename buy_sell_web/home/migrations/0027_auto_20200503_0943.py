# Generated by Django 3.0.5 on 2020-05-03 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_auto_20200503_0915'),
    ]

    operations = [
        migrations.RunSQL('ALTER TABLE home_orders_without_trxid AUTO_INCREMENT = 103005;')
    ]