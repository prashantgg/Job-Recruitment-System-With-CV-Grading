# Generated by Django 5.1.4 on 2025-03-08 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JRS', '0029_alter_hr_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hr',
            name='profile_picture',
            field=models.ImageField(default='profile_pictures/me.jpeg', upload_to='profile_pictures/'),
        ),
    ]
