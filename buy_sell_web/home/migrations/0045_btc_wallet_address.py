# Generated by Django 3.0.5 on 2020-06-01 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0044_actual_cash_flow_account_wise_actual_cash_flow_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='BTC_wallet_address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('belonging_order_id', models.IntegerField()),
            ],
        ),
    ]
