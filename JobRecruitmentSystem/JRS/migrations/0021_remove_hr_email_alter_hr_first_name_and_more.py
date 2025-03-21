# Generated by Django 5.1.4 on 2025-03-05 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JRS', '0020_alter_hr_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hr',
            name='email',
        ),
        migrations.AlterField(
            model_name='hr',
            name='first_name',
            field=models.CharField(default='HR', max_length=255),
        ),
        migrations.AlterField(
            model_name='hr',
            name='last_name',
            field=models.CharField(default='User', max_length=255),
        ),
        migrations.AlterField(
            model_name='hr',
            name='profile_picture',
            field=models.ImageField(default='profile_pictures/default.png', upload_to='profile_pictures/'),
        ),
        migrations.AlterField(
            model_name='hr',
            name='username',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
