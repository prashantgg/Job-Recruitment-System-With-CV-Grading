from django.db import models
from django.contrib.auth.models import User  # Importing the built-in User model



class ContactForm(models.Model):
    name = models.CharField(max_length=50, default=0)
    email = models.EmailField(default=0)
    number = models.CharField(max_length=10,default=0)
    message = models.TextField(default=0)


    def __str__(self):
        return f"Message by {self.name}"

class HR(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, default='Default User Name')
    first_name = models.CharField(max_length=100, default='Default HR First Name')
    last_name = models.CharField(max_length=100, default='Default HR Last Name')
    email = models.EmailField(unique=True, default='default@email.com')

    def __str__(self):
        return self.first_name + " " + self.last_name

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, default='Default User Name')
    first_name = models.CharField(max_length=100, default='Default Candidate First Name')
    last_name = models.CharField(max_length=100, default='Default Candidate Last Name')
    email = models.EmailField(unique=True, default='default@email.com')
    skills = models.ManyToManyField(Skill, related_name="candidates")  # Change from TextField

    def __str__(self):
        return self.first_name + " " + self.last_name