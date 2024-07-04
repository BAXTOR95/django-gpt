# Generated by Django 5.0.6 on 2024-07-04 00:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='preferred_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chat.llmmodel'),
        ),
    ]