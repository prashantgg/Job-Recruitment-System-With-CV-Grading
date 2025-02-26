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
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default_profile.png')

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
    
class Feedback(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    email = models.EmailField()
    feedback = models.TextField()

    def __str__(self):
        return f"Feedback from {self.name}"
    

class Job(models.Model):
    JOB_TYPES = (
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
        ('Freelance', 'Freelance'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPES)
    salary = models.CharField(max_length=255)
    experience = models.CharField(max_length=255)
    skills = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    deadline = models.DateField()
    posted_by = models.ForeignKey('HR', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class JobApplication(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')  # Resume upload feature
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'job')  # Prevent duplicate applications

    def __str__(self):
        return f"{self.candidate.first_name} applied for {self.job.title}"