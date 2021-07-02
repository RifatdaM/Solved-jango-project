# Generated by Django 3.0.5 on 2020-05-16 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0038_conversion_rates'),
    ]

    operations = [
        migrations.CreateModel(
            name='conversion_rate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('skrill', models.FloatField()),
                ('neteller', models.FloatField()),
                ('paypal', models.FloatField()),
                ('payoneer', models.FloatField()),
                ('btcusd', models.FloatField()),
                ('bkash', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='conversion_rates',
        ),
    ]