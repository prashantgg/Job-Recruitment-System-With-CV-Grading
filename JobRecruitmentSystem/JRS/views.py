from io import BytesIO
import json
import re
from JRS.cv_grading import compute_similarity
import pdfkit # type: ignore
from django.contrib.auth import authenticate, login,logout
from django.db import IntegrityError
from .import models 
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from .models import CvGrading, InterviewSchedule, Job, JobApplication, User, HR, Candidate, Skill
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from JRS.decorators import hr_or_candidate_required, hr_required, candidate_required
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.sessions.backends.db import SessionStore
from django.http import FileResponse, HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.cache import never_cache






@never_cache
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
@never_cache
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


@never_cache
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


@never_cache
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


@never_cache
@login_required
def logout_user(request):
    if not request.user.is_superuser:  # Do not log out superuser
        logout(request)
    messages.error(request, "Logged Out Successfully")
    return redirect("JRS:hr_login_page", permanent=True)
@never_cache
@login_required
def logout_users(request):
    if not request.user.is_superuser:  # Do not log out superuser
        logout(request)
    messages.error(request, "Logged Out Successfully")
    return redirect("JRS:candidate_login_page", permanent=True)
@never_cache
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
@never_cache
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

@never_cache
def startpage(request):
    return render(request, "JRS/startpage.html")





@never_cache
def aboutpage(request):
    return render(request, "JRS/aboutpage.html")


@never_cache
def featurepage(request):
    return render(request, "JRS/featurepage.html")
@never_cache
@login_required
@hr_required
def feedback(request):
    return render(request, "JRS/feedback.html")
@never_cache
@login_required
@candidate_required
def feedback_candidate(request):
    return render(request, "JRS/feedback_candidate.html")
@never_cache
def contactpage(request):
    return render(request, "JRS/contactpage.html")

@never_cache
@login_required
@candidate_required
def candidate_dashboard(request):
    return render(request, "JRS/candidate_dashboard.html")
@never_cache
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


@never_cache
def faqpage(request):
    return render(request, "JRS/faqpage.html")


@never_cache
def blogpage(request):
    return render(request, "JRS/blogpage.html")


@never_cache
def hr_register_page(request):
    return render(request, "JRS/hr_register_page.html")
@never_cache
def candidate_register_page(request):
    return render(request, "JRS/candidate_register_page.html")
@never_cache
def job_listing(request):
     jobs = Job.objects.all  # Filter jobs posted by this HR
     return render(request, 'JRS/job_listing.html', {'jobs': jobs})

@never_cache
def hr_login_page(request):
    return render(request, "JRS/hr_login_page.html")
@never_cache
def candidate_login_page(request):
    return render(request, "JRS/candidate_login_page.html")


@never_cache
@login_required
@hr_required
def job_update_page(request):
    return render(request, "JRS/update_job.html")
@never_cache
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
    

@never_cache# This view is for HR to see only the jobs they posted
@login_required
@hr_required
def view_jobs(request):
    if hasattr(request.user, 'hr'):  # Check if the user is an HR
        hr = request.user.hr  # Get the HR instance linked to this user
        jobs = Job.objects.filter(posted_by=hr)  # Filter jobs posted by this HR
        return render(request, 'JRS/view_job.html', {'jobs': jobs})
    else:
        return render(request, 'error.html')  # Show an error or redirect if the user is not HR
@never_cache   
@login_required
@candidate_required
def view_applications(request):
    # Get the candidate's applications
    applications = JobApplication.objects.filter(candidate=request.user.candidate)
    return render(request, 'JRS/view_applications.html', {'applications': applications})

@never_cache
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
            return redirect('JRS:post_jobs')

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
        return redirect('JRS:post_jobs')  # Redirect to HR dashboard after posting the job

    return render(request, 'JRS/post_job.html')  # Render the post job page
@never_cache
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
@never_cache
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



@never_cache
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

@never_cache
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
@never_cache
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
@never_cache
@login_required
@candidate_required
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    skills = job.skill_list()  # Call the method to process skills
    return render(request, 'JRS/view_job_detail.html', {'job': job, 'skills': skills})
@never_cache
@login_required
@hr_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    skills = job.skill_list()  # Call the method to process skills
    return render(request, 'JRS/view_detail.html', {'job': job, 'skills': skills})

@never_cache
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
@never_cache
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

@never_cache
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

@never_cache
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
@never_cache
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
@never_cache
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





@never_cache
@login_required
@hr_required
def posted_jobs(request):
    """ Display jobs posted by the logged-in HR """
    if hasattr(request.user, 'hr'):
        jobs = Job.objects.filter(posted_by=request.user.hr)
    else:
        jobs = None

    return render(request, 'JRS/posted_jobs.html', {'jobs': jobs})

@never_cache
@login_required
@hr_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    applications = JobApplication.objects.filter(job=job).select_related('candidate')

    return render(request, 'JRS/view_applicants.html', {
        'job': job,
        'applications': applications
    })




from django.template.loader import render_to_string
@never_cache
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

@hr_required
@login_required
@never_cache
@login_required
def job_list(request):
    # Get the logged-in HR user
    hr = request.user.hr  # Assuming the HR model is related to the User model (OneToOneField)
    # Get the jobs posted by the logged-in HR
    jobs = Job.objects.filter(posted_by=hr)
    return render(request, 'JRS/list_job.html', {'jobs': jobs})


@hr_required
@login_required
@never_cache
def view_graded_scores(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    graded_applications = CvGrading.objects.filter(application__job=job)

    return render(request, "JRS/view_graded_score.html", {
        "job": job,
        "graded_applications": graded_applications
    })

@login_required
@hr_required
# Accept an application
def accept_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    application.status = 'Accepted'
    application.save()
    
    # Optional: Send feedback or a notification to the candidate (can be added here)
    messages.success(request, f"Application for {application.candidate.first_name} has been accepted.")
    
    return redirect('JRS:view_graded_scores', job_id=application.job.id)  # Redirect to the graded applicants page for the job


@login_required
@hr_required
def reject_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    application.status = 'Rejected'
    application.save()

    # Optional: Send feedback or a notification to the candidate (can be added here)
    messages.error(request, f"Application for {application.candidate.first_name} has been rejected.")
    
    return redirect('JRS:view_graded_scores', job_id=application.job.id)  # Redirect to the graded applicants page for the job


@login_required
@hr_required
def candidate_jobs(request):
    # Ensure request.user is an HR instance
    hr_instance = HR.objects.filter(user=request.user).first()
    if not hr_instance:
        return HttpResponse("You are not authorized to view this page.", status=403)

    # Get jobs posted by this HR
    my_jobs = Job.objects.filter(posted_by=hr_instance)

    # Add applied and accepted candidate counts
    for job in my_jobs:
        job.total_applied = JobApplication.objects.filter(job=job).count()
        job.accepted_count = JobApplication.objects.filter(job=job, status="Accepted").count()

    return render(request, "JRS/accepted_job.html", {"my_jobs": my_jobs})


@login_required
@hr_required
def schedule_interview(request, job_id):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        interview_date = request.POST.get("interview_date")

        # Fetch the candidate application and update the interview date in InterviewSchedule model
        candidate_application = get_object_or_404(JobApplication, id=candidate_id, job_id=job_id)
        
        # Create or update the InterviewSchedule model
        interview_schedule, created = InterviewSchedule.objects.get_or_create(
            candidate=candidate_application.candidate,
            job=candidate_application.job,
            defaults={'scheduled_date': interview_date, 'status': 'Scheduled'}
        )

        if not created:
            # If an interview schedule already exists, update it
            interview_schedule.scheduled_date = interview_date
            interview_schedule.status = 'Scheduled'
            interview_schedule.save()

        # Display a success message
        messages.success(
            request,
            f"Interview scheduled for {candidate_application.candidate.user.first_name} on {interview_date}!"
        )
        return redirect("JRS:schedule_interview", job_id=job_id)

    # Fetch accepted candidates for the given job_id
    accepted_candidates = JobApplication.objects.filter(job_id=job_id, status="Accepted").select_related('candidate')

    # Collect CV grading and interview status for each accepted candidate
    candidates_with_details = []
    for application in accepted_candidates:
        grading = CvGrading.objects.filter(application=application).first()
        interview_schedule = InterviewSchedule.objects.filter(candidate=application.candidate, job=application.job).first()

        candidates_with_details.append({
            "application": application,
            "cv_score": grading.score if grading else "Not Graded",
            "cv_recommendation": grading.recommendation if grading else "Not Graded",
            "interview_status": interview_schedule.status if interview_schedule else "Not Scheduled",  # Interview status
            "scheduled_date": interview_schedule.scheduled_date if interview_schedule else "Not Scheduled",  # Scheduled date
        })

    # Render the template with the necessary context
    return render(
        request,
        "JRS/schedule_interview.html",
        {"candidates_with_details": candidates_with_details, "job_id": job_id}
    )

from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models.functions import ExtractMonth


import calendar
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import HR, Job, JobApplication
from .decorators import hr_required

@login_required
@hr_required
def hr_dashboard(request):
    try:
        hr_user = HR.objects.get(user=request.user)
    except HR.DoesNotExist:
        return render(request, 'JRS/error.html', {'message': 'HR Profile not found.'})

    # Total job posts by HR
    total_jobs = Job.objects.filter(posted_by=hr_user).count()

    # Total applicants
    total_applicants = JobApplication.objects.filter(job__posted_by=hr_user).count()

    # Application status counts
    total_accepted = JobApplication.objects.filter(job__posted_by=hr_user, status="Accepted").count() or 0
    total_rejected = JobApplication.objects.filter(job__posted_by=hr_user, status="Rejected").count() or 0
    total_pending = JobApplication.objects.filter(job__posted_by=hr_user, status="Pending").count() or 0

    # Fetch job post and applicant data by month
    job_post_data = Job.objects.filter(posted_by=hr_user).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(count=Count('id'))

    applicants_data = JobApplication.objects.filter(job__posted_by=hr_user).annotate(
        month=ExtractMonth('applied_at')
    ).values('month').annotate(count=Count('id'))

    # Convert month numbers (1-12) to short month names (Jan, Feb, ...)
    months = [calendar.month_abbr[i] for i in range(1, 13)]

    # Convert query results into dictionaries
    job_posts = {calendar.month_abbr[data["month"]]: data["count"] for data in job_post_data}
    applicants = {calendar.month_abbr[data["month"]]: data["count"] for data in applicants_data}

    # Prepare data lists for charts
    job_posts_list = [job_posts.get(month, 0) for month in months]
    applicants_list = [applicants.get(month, 0) for month in months]

    context = {
        "total_jobs": total_jobs,
        "total_applicants": total_applicants,
        "total_accepted": total_accepted,
        "total_rejected": total_rejected,
        "total_pending": total_pending,
        "months": months,
        "job_posts_list": job_posts_list,
        "applicants_list": applicants_list,
    }

    return render(request, "JRS/hr_dashboard.html", context)



















        