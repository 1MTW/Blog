# Generated by Django 4.2.17 on 2025-01-06 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("llmapp", "0002_uploadedpdf_processing_progress"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatsession",
            name="history",
            field=models.JSONField(default=list),
        ),
    ]
