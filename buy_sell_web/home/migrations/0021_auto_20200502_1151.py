# Generated by Django 3.0.5 on 2020-05-02 11:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import home.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0020_files'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('file2', models.FileField(upload_to='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='profile_info',
            name='profile_status',
            field=models.CharField(choices=[('not_verified', 'not_verified'), ('verified', 'verified'), ('pending', 'pending')], default='pending', max_length=100),
        ),
        migrations.DeleteModel(
            name='Files',
        ),
    ]
