from io import BytesIO
import re
import pdfkit # type: ignore
from django.contrib.auth import authenticate, login,logout
from django.db import IntegrityError
from .import models 
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from .models import Job, JobApplication, User, HR, Candidate, Skill
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from JRS.decorators import hr_or_candidate_required, hr_required, candidate_required
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.sessions.backends.db import SessionStore
from django.http import FileResponse, HttpResponse
from django.core.files.storage import default_storage





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

            # ✅ Add user to Candidate group (Fixing previous mistake)
            hr_group, created = Group.objects.get_or_create(name="HR")
            user.groups.add(hr_group)

            # Create the HR profile
            hr = HR.objects.create(user=user, username=username, first_name=first_name, last_name=last_name, email=email)

            # ✅ Display success message
            messages.success(request, "HR Account Created Successfully!")

            # Redirect to HR register page or login page
            return redirect("JRS:hr_login_page")

        except IntegrityError:
            messages.error(request, "Username or email already exists for an HR profile.")
            return redirect("JRS:hr_register_page")

    return render(request, "JRS/hr_register_page.html")

def hr_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                hr_user = HR.objects.get(user=user)
                if hr_user.user.email == email:
                    
                    # Ensure superuser session is not overridden
                    if not user.is_superuser:
                        request.session = SessionStore()

                    login(request, user)
                    messages.success(request, "HR Logged In Successfully")
                    return redirect("JRS:hr_dashboard")
                else:
                    messages.error(request, "Invalid email address.")
                    return redirect("JRS:hr_login_page")
            except HR.DoesNotExist:
                messages.error(request, "Access Denied: You are not an HR user.")
                return redirect("JRS:hr_login_page")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("JRS:hr_login_page")

    return render(request, "JRS/hr_login_page.html")



def candidate_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                candidate_user = Candidate.objects.get(user=user)
                if candidate_user.user.email == email:
                    
                    # Ensure superuser session is not overridden
                    if not user.is_superuser:
                        request.session = SessionStore()

                    login(request, user)
                    messages.success(request, "Candidate Logged In Successfully")
                    return redirect("JRS:candidate_dashboard")
                else:
                    messages.error(request, "Invalid email address.")
                    return redirect("JRS:candidate_login_page")
            except Candidate.DoesNotExist:
                messages.error(request, "Access Denied: You are not a Candidate user.")
                return redirect("JRS:candidate_login_page")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("JRS:candidate_login_page")

    return render(request, "JRS/candidate_login_page.html")



def candidate_registration(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        skills = request.POST.get("skills", "").split(",")

        if Candidate.objects.filter(username=username).exists():
            messages.error(request, "Username already exists for a Candidate profile.")
            return redirect("JRS:candidate_register_page")

        if Candidate.objects.filter(email=email).exists():
            messages.error(request, "A Candidate profile with this email already exists.")
            return redirect("JRS:candidate_register_page")

        try:
            # ✅ Create User
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            user.save()

            # ✅ Assign to Candidate Group
            candidate_group, created = Group.objects.get_or_create(name="Candidate")
            user.groups.add(candidate_group)

            # Debugging: Print group info
            print(f"✅ User {user.username} added to groups: {user.groups.all()}")  

            # ✅ Create Candidate Profile
            candidate = Candidate.objects.create(
                user=user, 
                username=username, 
                first_name=first_name, 
                last_name=last_name, 
                email=email
            )

            # ✅ Process skills safely
            skill_objects = []
            for skill in skills:
                skill = skill.strip()
                if skill:  
                    skill_obj, created = Skill.objects.get_or_create(name=skill)
                    skill_objects.append(skill_obj)

            candidate.skills.set(skill_objects)  

            messages.success(request, "Candidate Account Created Successfully!")
            return redirect("JRS:candidate_login_page")

        except IntegrityError:
            messages.error(request, "Username already exists.")
            return redirect("JRS:candidate_register_page")

    return render(request, "JRS/candidate_register_page.html")



@login_required
def logout_user(request):
    if not request.user.is_superuser:  # Do not log out superuser
        logout(request)
    messages.error(request, "Logged Out Successfully")
    return redirect("JRS:hr_login_page", permanent=True)

@login_required
def logout_users(request):
    if not request.user.is_superuser:  # Do not log out superuser
        logout(request)
    messages.error(request, "Logged Out Successfully")
    return redirect("JRS:candidate_login_page", permanent=True)

@login_required
@hr_required
def submit_feedback_hr(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        feedback = request.POST['feedback']
        
        # Save feedback to database
        models.Feedback.objects.create(name=name, email=email, contact=contact, feedback=feedback)
        
        # Show a success message
        messages.success(request, "Your feedback has been submitted successfully!")
        return redirect('JRS:feedback_hr_page')  # Redirect back to the feedback page
    return render(request, 'JRS/feedback.html')

@login_required
@candidate_required
def submit_feedback_candidate(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        feedback = request.POST['feedback']
        
        # Save feedback to database
        models.Feedback.objects.create(name=name, email=email, contact=contact, feedback=feedback)
        
        # Show a success message
        messages.success(request, "Your feedback has been submitted successfully!")
        return redirect('JRS:feedback_candidate_page')  # Redirect back to the feedback page
    return render(request, 'JRS/feedback_candidate.html')


def startpage(request):
    return render(request, "JRS/startpage.html")

@login_required
@hr_required
def post_job(request):
    return render(request, "JRS/post_job.html")




def aboutpage(request):
    return render(request, "JRS/aboutpage.html")



def featurepage(request):
    return render(request, "JRS/featurepage.html")

@login_required
@hr_required
def feedback(request):
    return render(request, "JRS/feedback.html")
@login_required
@candidate_required
def feedback_candidate(request):
    return render(request, "JRS/feedback_candidate.html")

def contactpage(request):
    return render(request, "JRS/contactpage.html")

@login_required
@hr_required
def hr_dashboard(request):
    return render(request, "JRS/hr_dashboard.html")

@login_required
@candidate_required
def candidate_dashboard(request):
    return render(request, "JRS/candidate_dashboard.html")

@login_required
@candidate_required
def available_jobs(request):
    user = request.user
    try:
        candidate = Candidate.objects.get(user=user)
        candidate_skills = ", ".join([skill.name for skill in candidate.skills.all()])
    except Candidate.DoesNotExist:
        candidate_skills = ""

    jobs = Job.objects.all()

    job_skills_list = [job.skills for job in jobs]
    job_skills_list.append(candidate_skills)  # Append candidate skills for similarity calculation

    # Vectorize skills using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(job_skills_list)

    # Compute cosine similarity between candidate skills and job skills
    candidate_vector = tfidf_matrix[-1]  # Last vector is the candidate's skills
    job_vectors = tfidf_matrix[:-1]  # All other vectors are job skills

    similarity_scores = cosine_similarity(candidate_vector, job_vectors).flatten()

    # Attach similarity scores to jobs and sort in descending order
    job_with_scores = list(zip(jobs, similarity_scores))
    job_with_scores.sort(key=lambda x: x[1], reverse=True)

    sorted_jobs = [job for job, score in job_with_scores]

    # ✅ Ensure skills are processed for display
    for job in sorted_jobs:
        job.skill_list = job.skills.split(",")  # Convert comma-separated skills into a list

    return render(request, "JRS/available_jobs.html", {"jobs": sorted_jobs})



def faqpage(request):
    return render(request, "JRS/faqpage.html")



def blogpage(request):
    return render(request, "JRS/blogpage.html")



def hr_register_page(request):
    return render(request, "JRS/hr_register_page.html")

def candidate_register_page(request):
    return render(request, "JRS/candidate_register_page.html")

def job_listing(request):
     jobs = Job.objects.all  # Filter jobs posted by this HR
     return render(request, 'JRS/job_listing.html', {'jobs': jobs})


def hr_login_page(request):
    return render(request, "JRS/hr_login_page.html")

def candidate_login_page(request):
    return render(request, "JRS/candidate_login_page.html")



@login_required
@hr_required
def job_update_page(request):
    return render(request, "JRS/update_job.html")

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
    

# This view is for HR to see only the jobs they posted
@login_required
@hr_required
def view_jobs(request):
    if hasattr(request.user, 'hr'):  # Check if the user is an HR
        hr = request.user.hr  # Get the HR instance linked to this user
        jobs = Job.objects.filter(posted_by=hr)  # Filter jobs posted by this HR
        return render(request, 'JRS/view_job.html', {'jobs': jobs})
    else:
        return render(request, 'error.html')  # Show an error or redirect if the user is not HR
    
@login_required
@candidate_required
def view_applications(request):
    # Get the candidate's applications
    applications = JobApplication.objects.filter(candidate=request.user.candidate)
    return render(request, 'JRS/view_applications.html', {'applications': applications})


@login_required
@hr_required
def post_jobs(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        location = request.POST.get('location')
        job_type = request.POST.get('job_type')
        salary = request.POST.get('salary')
        experience = request.POST.get('experience')
        skills = request.POST.get('skills')
        education = request.POST.get('education')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        posted_by = request.user.hr  # Assuming HR model is linked to User via OneToOne

        # Validation checks
        if not title or not company or not location or not job_type or not salary or not experience or not skills or not education or not description or not deadline:
            messages.error(request, "All fields are required.")
            return redirect('JRS:post_job')

        # Save the job posting to the database
        job = models.Job(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            salary=salary,
            experience=experience,
            skills=skills,
            education=education,
            description=description,
            deadline=deadline,
            posted_by=posted_by
        )
        job.save()

        messages.success(request, "Job posted successfully!")
        return redirect('JRS:post_job')  # Redirect to HR dashboard after posting the job

    return render(request, 'JRS/post_job.html')  # Render the post job page

@login_required
@hr_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Ensure that the logged-in user is the one who posted the job
    if hasattr(request.user, 'hr') and request.user.hr == job.posted_by:
        job.delete()
        messages.success(request, "Job post deleted successfully!")
    else:
        messages.error(request, "You are not authorized to delete this job post.")
    
    return redirect('JRS:view_jobs')  # Redirect to the list of jobs the HR posted

@login_required
@candidate_required
def delete_application(request, application_id):
    candidate = Candidate.objects.get(user=request.user)  # Ensure user is treated as Candidate

    application = get_object_or_404(JobApplication, id=application_id, candidate=candidate)

    if request.method == "POST":
        application.delete()
        messages.success(request, "Application deleted successfully.")
        return redirect("JRS:view_applications")  # Ensure this URL is correct

    messages.error(request, "Invalid request.")
    return redirect("JRS:view_applications")




@login_required
@hr_required
def update_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.company = request.POST.get('company')
        job.location = request.POST.get('location')
        job.job_type = request.POST.get('job_type')
        job.salary = request.POST.get('salary')
        job.experience = request.POST.get('experience')
        job.skills = request.POST.get('skills')
        job.education = request.POST.get('education')
        job.deadline = request.POST.get('deadline')
        job.description = request.POST.get('description')
        job.save()
        
        # Optionally, add a success message
        messages.success(request, 'Job updated successfully!')
        return redirect('JRS:view_jobs')  # Redirect to job list after update

    return render(request, 'JRS/update_job.html', {'job': job})


@login_required
@candidate_required
def update_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, candidate__user=request.user)

    if request.method == 'POST':
        # Update resume if a new file is uploaded
        if 'resume' in request.FILES:
            application.resume = request.FILES['resume']

        # Update cover letter if provided
        application.cover_letter = request.POST.get('cover_letter', application.cover_letter)
        
        application.save()

        messages.success(request, 'Application updated successfully!')
        return redirect('JRS:view_applications')  # Redirect to application list after update

    return render(request, 'JRS/update_applications.html', {'application': application})

@login_required
@candidate_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Ensure the logged-in user is a Candidate
    if not hasattr(request.user, 'candidate'):
        messages.error(request, "Only candidates can apply for jobs.")
        return redirect('JRS:available_jobs')

    candidate = request.user.candidate

    # Prevent duplicate applications
    if JobApplication.objects.filter(candidate=candidate, job=job).exists():
        messages.error(request, 'You Have Already Applied for this Job')
        return redirect('JRS:available_jobs')

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')

        if not cover_letter or not resume:
            messages.error(request, "Both cover letter and resume are required.")
            return redirect('JRS:apply_job', job_id=job.id)

        # Save the application
        job_application = JobApplication(
            candidate=candidate,
            job=job,
            cover_letter=cover_letter,
            resume=resume
        )
        job_application.save()

        messages.success(request, f"You have applied for {job.title} job")
        return redirect('JRS:available_jobs')

    return render(request, 'JRS/apply_job.html', {'job': job})

@login_required
@candidate_required
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    skills = job.skill_list()  # Call the method to process skills
    return render(request, 'JRS/view_job_detail.html', {'job': job, 'skills': skills})

@login_required
@hr_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    skills = job.skill_list()  # Call the method to process skills
    return render(request, 'JRS/view_detail.html', {'job': job, 'skills': skills})



def job_listing(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Filtering jobs by title or skills
        jobs = Job.objects.filter(
            title__icontains=search_query
        ) | Job.objects.filter(
            skills__icontains=search_query
        )
    else:
        jobs = Job.objects.all()
    
    return render(request, 'JRS/job_listing.html', {'jobs': jobs})

@candidate_required
@login_required
def list_job(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Filtering jobs by title or skills
        jobs = Job.objects.filter(
            title__icontains=search_query
        ) | Job.objects.filter(
            skills__icontains=search_query
        )
    else:
        jobs = Job.objects.all()
    
    return render(request, 'JRS/available_jobs.html', {'jobs': jobs})


@login_required(login_url="JRS:candidate_login")  # Redirects to HR login page if not logged in
@candidate_required
def change_password_candidate(request):
    if request.method == "POST":
        o_pass = request.POST.get("o_pass")
        n_pass = request.POST.get("n_pass")
        c_pass = request.POST.get("c_pass")


        # Check if any of the password fields are missing
        if not o_pass or not n_pass or not c_pass:
            messages.error(request, "All fields are required.")
            return redirect("JRS:change_password_candidate")
        
        # Validate the new password format using regex
        if not re.search(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$', n_pass):
            messages.error(request, "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character (@$!%*?&).")
            return redirect("JRS:change_password_candidate", permanent=True)
        
        if n_pass == c_pass:
            user = request.user
            if user.check_password(o_pass):
                user.set_password(n_pass)
                user.save()
                messages.success(request, "Password has been changed successfully. Please log in again.")
                return redirect("JRS:candidate_login_page")  # Redirect HR to log in again
            else:
                messages.error(request, "Your old password is incorrect. Please enter the correct one.")
        else:
            messages.error(request, "New password and confirm password do not match.")
    
    return render(request, "JRS/change_password_candidate.html")


@login_required(login_url="JRS:hr_login")  # Redirects to HR login page if not logged in
@hr_required
def change_password_hr(request):
    if request.method == "POST":
        o_pass = request.POST.get("o_pass")
        n_pass = request.POST.get("n_pass")
        c_pass = request.POST.get("c_pass")

        # Check if any of the password fields are missing
        if not o_pass or not n_pass or not c_pass:
            messages.error(request, "All fields are required.")
            return redirect("JRS:change_password_hr")

        # Validate the new password format using regex
        if not re.search(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$', n_pass):
            messages.error(request, "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character (@$!%*?&).")
            return redirect("JRS:change_password_hr")

        if n_pass == c_pass:
            user = request.user
            if user.check_password(o_pass):
                user.set_password(n_pass)
                user.save()
                messages.success(request, "Password has been changed successfully. Please log in again.")
                return redirect("JRS:hr_login_page")  # Redirect HR to log in again
            else:
                messages.error(request, "Your old password is incorrect.")
        else:
            messages.error(request, "New password and confirm password do not match.")

    return render(request, "JRS/change_password_hr.html")


from django.core.files.storage import FileSystemStorage

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@login_required
@hr_required
def edit_hr_profile(request):
    hr = HR.objects.get(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        # Update only if fields are provided
        if first_name:
            hr.first_name = first_name
        if last_name:
            hr.last_name = last_name
        if username:
            hr.username = username

        # Handle profile picture upload
        if profile_picture:
            file_path = f"profile_pictures/{profile_picture.name}"

            # Delete old picture (except default)
            if hr.profile_picture and hr.profile_picture.name != "profile_pictures/default.png":
                if default_storage.exists(hr.profile_picture.name):
                    default_storage.delete(hr.profile_picture.name)

            # Save new profile picture
            hr.profile_picture.save(file_path, ContentFile(profile_picture.read()))

        hr.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("JRS:edit_profile_hr")

    return render(request, "JRS/edit_profile_hr.html", {"hr": hr})

@login_required
@candidate_required
def edit_candidate_profile(request):
    candidate = Candidate.objects.get(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        # Update only if fields are provided
        if first_name:
            candidate.first_name = first_name
        if last_name:
            candidate.last_name = last_name
        if username:
            candidate.username = username

        # Handle profile picture upload
        if profile_picture:
            file_path = f"profile_pictures/{profile_picture.name}"

            # Delete old picture (except default)
            if candidate.profile_picture and candidate.profile_picture.name != "profile_pictures/default.png":
                if default_storage.exists(candidate.profile_picture.name):
                    default_storage.delete(candidate.profile_picture.name)

            # Save new profile picture
            candidate.profile_picture.save(file_path, ContentFile(profile_picture.read()))

        candidate.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("JRS:edit_profile_candidate")

    return render(request, "JRS/edit_profile_candidate.html", {"candidate": candidate})






@login_required
@hr_required
def posted_jobs(request):
    """ Display jobs posted by the logged-in HR """
    if hasattr(request.user, 'hr'):
        jobs = Job.objects.filter(posted_by=request.user.hr)
    else:
        jobs = None

    return render(request, 'JRS/posted_jobs.html', {'jobs': jobs})


@login_required
@hr_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    applications = JobApplication.objects.filter(job=job)

    return render(request, 'JRS/view_applicants.html', {
        'job': job,
        'applications': applications
    })



from django.template.loader import render_to_string

def generate_cover_letter_pdf(request, application_id):
    application = get_object_or_404(JobApplication, pk=application_id)
    
    # Generate HTML content from the template
    html_content = render_to_string('JRS/your_template_name.html', {'application': application})
    
    # Create a PDF from the generated HTML string
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(html_content, False, configuration=config)
    
    # Return the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cover_letter.pdf"'
    
    return response
















        