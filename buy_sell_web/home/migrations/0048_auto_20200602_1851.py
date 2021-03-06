# Generated by Django 3.0.5 on 2020-06-02 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0047_orders_without_trxid_admin_receiving_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_with_trxid',
            name='admin_transaction_id',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='order_with_trxid',
            name='order_processed_by',
            field=models.IntegerField(default=0),
        ),
    ]
