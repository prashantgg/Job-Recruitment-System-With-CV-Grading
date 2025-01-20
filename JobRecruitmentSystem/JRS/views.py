from django.http import HttpResponse
from django.shortcuts import render
from .import models 


# Create your views here.
def startpage(request):
    return render(request, "JRS/startpage.html")

def aboutpage(request):
    return render(request, "JRS/aboutpage.html")

def featurepage(request):
    return render(request, "JRS/featurepage.html")

def contactpage(request):
    return render(request, "JRS/contactpage.html")

def faqpage(request):
    return render(request, "JRS/faqpage.html")

def blogpage(request):
    return render(request, "JRS/blogpage.html")

def hr_register_page(request):
    return render(request, "JRS/hr_register_page.html")

def contact_form(request):
    if request.method == "POST":
        # Get form data from POST request
        name = request.POST.get("name")
        email = request.POST.get("email")
        number = request.POST.get("phone")
        message = request.POST.get("message")
        print (name,email,number,message)
        # Create and save the new contact entry
        contact = models.ContactForm(name=name, email=email, number=number, message=message)
        contact.save()   

        return render(request, 'JRS/contactpage.html')


        
