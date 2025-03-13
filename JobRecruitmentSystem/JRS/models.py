import datetime
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
    first_name = models.CharField(max_length=255, null=False, blank=False, default="HR")
    last_name = models.CharField(max_length=255, null=False, blank=False, default="User")
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, default='default@email.com')
    profile_picture = models.ImageField(upload_to="profile_pictures/", default="profile_pictures/default.png")

    def __str__(self):
        return self.username



class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, default='Default User Name')
    first_name = models.CharField(max_length=100, default='Default Candidate First Name',null=False, blank=False,)
    last_name = models.CharField(max_length=100, default='Default Candidate Last Name',null=False, blank=False,)
    email = models.EmailField(unique=True, default='default@email.com')
    skills = models.ManyToManyField(Skill, related_name="candidates")  # Change from TextField
    profile_picture = models.ImageField(upload_to="profile_pictures/", default="profile_pictures/default.png")


    def __str__(self):
        return self.first_name + " " + self.last_name
    
class Feedback(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    email = models.EmailField()
    feedback = models.TextField()

    def __str__(self):
        return f"Feedback from {self.name}"
    

from django.utils.timezone import now

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

    def skill_list(self):
        """ Convert the comma-separated skills into a list """
        return [skill.strip() for skill in self.skills.split(',')] if self.skills else []


    
class JobApplication(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    cover_letter_file = models.FileField(upload_to='cover_letters/', blank=True, null=True)  
    applied_at = models.DateTimeField(auto_now_add=True)
    is_graded = models.BooleanField(default=False)  # New field to track CV grading
    status = models.CharField(max_length=20, choices=[('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Pending', 'Pending')], default='Pending')  # New field for status


    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"{self.candidate.first_name} applied for {self.job.title}"

    
class CvGrading(models.Model):
    
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='grading')
    score = models.FloatField()  # Percentage (0-100)
    recommendation = models.CharField(max_length=50)  # "Highly Recommended", "Moderately Recommended", "Not Recommended"
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.candidate.first_name} - {self.application.job.title}: {self.score}%"
    

class InterviewSchedule(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed')], default='Scheduled')

    def __str__(self):
        return f"Interview for {self.candidate.user.username} - {self.job.title} on {self.scheduled_date}"
