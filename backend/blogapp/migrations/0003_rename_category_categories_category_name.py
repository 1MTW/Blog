# Generated by Django 4.2.17 on 2025-01-11 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0002_categories_alter_posthistory_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categories',
            old_name='category',
            new_name='category_name',
        ),
    ]