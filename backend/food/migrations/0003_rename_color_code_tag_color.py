# Generated by Django 3.2.16 on 2024-03-29 06:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0002_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='color_code',
            new_name='color',
        ),
    ]