# Generated by Django 5.1.4 on 2025-03-14 12:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JRS', '0036_interviewfeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='interview',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='JRS.interviewschedule'),
        ),
    ]
