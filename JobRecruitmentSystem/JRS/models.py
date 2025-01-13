from django.db import models

class ContactForm(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    number = models.CharField(max_length=10)
    message = models.TextField()


    def __str__(self):
        return f"Message by {self.name}"