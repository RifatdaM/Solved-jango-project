# Generated by Django 3.0.5 on 2020-06-15 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0055_auto_20200611_1758'),
    ]

    operations = [
        migrations.CreateModel(
            name='We_rcv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('unit', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='We_send',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('unit', models.CharField(max_length=15)),
            ],
        ),
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