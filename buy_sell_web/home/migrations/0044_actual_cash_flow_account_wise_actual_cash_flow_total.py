# Generated by Django 3.0.5 on 2020-05-31 19:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0043_auto_20200601_0052'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actual_cash_flow_account_wise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('gateway', models.CharField(max_length=100)),
                ('account_name', models.CharField(max_length=100)),
                ('incoming', models.FloatField()),
                ('outgoing', models.FloatField()),
                ('belonging_order_id', models.IntegerField()),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Actual_cash_flow_total',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('incoming', models.FloatField()),
                ('outgoing', models.FloatField()),
            ],
        ),
    ]
