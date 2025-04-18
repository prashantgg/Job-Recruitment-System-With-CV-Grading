# Generated by Django 5.1.4 on 2025-03-14 12:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JRS', '0038_interviewschedule_feedback'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewfeedback',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='interviewfeedback',
            name='hr',
        ),
        migrations.RemoveField(
            model_name='interviewfeedback',
            name='interview',
        ),
        migrations.RemoveField(
            model_name='interviewfeedback',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='interviewschedule',
            name='feedback',
        ),
        migrations.AddField(
            model_name='interviewfeedback',
            name='feedback',
            field=models.TextField(default='No feedback provided yet'),
        ),
        migrations.AddField(
            model_name='interviewfeedback',
            name='job_application',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='JRS.jobapplication'),
        ),
    ]
