# Generated by Django 3.2.16 on 2024-04-03 11:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('food', '0004_auto_20240401_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='subscribed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribed', to=settings.AUTH_USER_MODEL, verbose_name='Блогеры'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
