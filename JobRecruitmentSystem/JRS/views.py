import re
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from .import models 
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from .models import User, HR, Candidate, Skill
from django.contrib import messages
from django.contrib.auth.decorators import login_required




# HR Registration View
def hr_registration(request):
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']

        # ✅ Check if the username already exists in HR model (not User model)
        if HR.objects.filter(username=username).exists():
            messages.error(request, "Username already exists for an HR profile.")
            return redirect("JRS:hr_register_page")

        # ✅ Check if the email already exists in HR model
        if HR.objects.filter(email=email).exists():
            messages.error(request, "An HR profile with this email already exists.")
            return redirect("JRS:hr_register_page")

        try:
            # Create a new user (Even if the username exists in User model, it's fine)
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            user.save()

            # Create the HR profile
            hr = HR.objects.create(user=user, username=username, first_name=first_name, last_name=last_name, email=email)

            # ✅ Display success message
            messages.success(request, "HR Account Created Successfully!")

            # Redirect to HR register page or login page
            return redirect("JRS:hr_register_page")

        except IntegrityError:
            messages.error(request, "Username or email already exists for an HR profile.")
            return redirect("JRS:hr_register_page")

    return render(request, "JRS/hr_register_page.html")

def hr_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user using username
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user exists in the HR model and email matches
            try:
                hr_user = HR.objects.get(user=user)
                if hr_user.user.email == email:  # Validate email
                    login(request, user)
                    messages.success(request, "HR Logged In Successfully")
                    return redirect("JRS:hr_dashboard", permanent=True)
                else:
                    messages.error(request, "Invalid email address.")
                    return redirect("JRS:hr_login_page", permanent=True)
            except HR.DoesNotExist:
                messages.error(request, "Access Denied: You are not an HR user.")
                return redirect("JRS:hr_login_page", permanent=True)
        else:
            messages.error(request, "Invalid username or password")
            return redirect("JRS:hr_login_page", permanent=True)

    return render(request, "JRS/hr_dashboard.html")
def candidate_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user using username
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user exists in the HR model and email matches
            try:
                candidate_user = Candidate.objects.get(user=user)
                if candidate_user.user.email == email:  # Validate email
                    login(request, user)
                    messages.success(request, "Candidate Logged In Successfully")
                    return redirect("JRS:candidate_dashboard", permanent=True)
                else:
                    messages.error(request, "Invalid email address.")
                    return redirect("JRS:candidate_login_page", permanent=True)
            except Candidate.DoesNotExist:
                messages.error(request, "Access Denied: You are not an Candidate user.")
                return redirect("JRS:candidate_login_page", permanent=True)
        else:
            messages.error(request, "Invalid username or password")
            return redirect("JRS:candidate_login_page", permanent=True)

    return render(request, "JRS/candidate_dashboard.html")

# Candidate Registration View
def candidate_registration(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        skills = request.POST.get("skills", "").split(",")  # Get skills as a list

        # ✅ Check if username or email already exists in Candidate
        if Candidate.objects.filter(username=username).exists():
            messages.error(request, "Username already exists for a Candidate profile.")
            return redirect("JRS:candidate_register_page")

        if Candidate.objects.filter(email=email).exists():
            messages.error(request, "A Candidate profile with this email already exists.")
            return redirect("JRS:candidate_register_page")

        try:
            # ✅ Create User first
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            user.save()

            # ✅ Create Candidate and link it to User
            candidate = Candidate.objects.create(
                user=user, 
                username=username, 
                first_name=first_name, 
                last_name=last_name, 
                email=email
            )

            # ✅ Process skills
            skill_objects = [Skill.objects.get_or_create(name=skill.strip())[0] for skill in skills if skill.strip()]
            candidate.skills.set(skill_objects)  # Use .set() for ManyToManyField

            messages.success(request, "Candidate Account Created Successfully!")
            return redirect("JRS:candidate_register_page")

        except IntegrityError:
            messages.error(request, "Username already exists.")
            return redirect("JRS:candidate_register_page")

    return render(request, "JRS/candidate_register_page.html")

def submit_feedback(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        feedback = request.POST['feedback']
        
        # Save feedback to database
        models.Feedback.objects.create(name=name, email=email, contact=contact, feedback=feedback)
        
        # Show a success message
        messages.success(request, "Your feedback has been submitted successfully!")
        return redirect('JRS:feedback_page')  # Redirect back to the feedback page
    return render(request, 'JRS/feedback.html')




# Create your views here.
def startpage(request):
    return render(request, "JRS/startpage.html")

def edit_profile_hr(request):
    return render(request, "JRS/edit_profile_hr.html")

def aboutpage(request):
    return render(request, "JRS/aboutpage.html")

def featurepage(request):
    return render(request, "JRS/featurepage.html")

def feedback(request):
    return render(request, "JRS/feedback.html")

def contactpage(request):
    return render(request, "JRS/contactpage.html")

def hr_dashboard(request):
    return render(request, "JRS/hr_dashboard.html")

def candidate_dashboard(request):
    return render(request, "JRS/candidate_dashboard.html")

def faqpage(request):
    return render(request, "JRS/faqpage.html")

def blogpage(request):
    return render(request, "JRS/blogpage.html")

def hr_register_page(request):
    return render(request, "JRS/hr_register_page.html")

def candidate_register_page(request):
    return render(request, "JRS/candidate_register_page.html")

def hr_login_page(request):
    return render(request, "JRS/hr_login_page.html")

def candidate_login_page(request):
    return render(request, "JRS/candidate_login_page.html")

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


        
