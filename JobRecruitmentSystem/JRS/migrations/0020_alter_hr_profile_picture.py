# Generated by Django 5.1.4 on 2025-03-04 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JRS', '0019_alter_hr_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hr',
            name='profile_picture',
            field=models.ImageField(default='profile_pictures/default_profile.png', upload_to='profile_pictures/'),
        ),
    ]
