# Generated by Django 3.0.5 on 2020-05-02 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_auto_20200502_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='files/'),
        ),
        migrations.AlterField(
            model_name='file',
            name='file2',
            field=models.FileField(upload_to='files/'),
        ),
    ]
