# Generated by Django 3.0.7 on 2020-06-15 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_we_rcv_we_send'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders_without_trxid',
            name='receive_at',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='orders_without_trxid',
            name='sent_from',
            field=models.CharField(max_length=100),
        ),
    ]