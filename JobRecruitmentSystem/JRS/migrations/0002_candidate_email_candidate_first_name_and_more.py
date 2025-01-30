# Generated by Django 5.1.4 on 2025-01-29 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JRS', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='email',
            field=models.EmailField(default='default@email.com', max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='first_name',
            field=models.CharField(default='Default Candidate First Name', max_length=100),
        ),
        migrations.AddField(
            model_name='candidate',
            name='last_name',
            field=models.CharField(default='Default Candidate Last Name', max_length=100),
        ),
        migrations.AddField(
            model_name='hr',
            name='email',
            field=models.EmailField(default='default@email.com', max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='hr',
            name='first_name',
            field=models.CharField(default='Default HR First Name', max_length=100),
        ),
        migrations.AddField(
            model_name='hr',
            name='last_name',
            field=models.CharField(default='Default HR Last Name', max_length=100),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='skills',
            field=models.TextField(default='No skills listed'),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='email',
            field=models.EmailField(default=0, max_length=254),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='message',
            field=models.TextField(default=0),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='name',
            field=models.CharField(default=0, max_length=50),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='number',
            field=models.CharField(default=0, max_length=10),
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
