from django.shortcuts import redirect
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "JRS"

urlpatterns = [
    path("home", views.startpage, name="startpage"),  # No space in the name
    path("about", views.aboutpage, name="aboutpage"),
    path('view-jobs/', views.view_jobs, name='view_jobs'),
    path('job/<int:job_id>/', views.view_jobs, name='job_detail'),  # New path for job detail
    path('job/update/<int:job_id>/', views.update_job, name='update_job'),
    path("feedback", views.feedback, name="feedback"),
    path("feature", views.featurepage, name="featurepage"),
    path("contact", views.contactpage, name="contactpage"),
    path('contact/', views.contact_form, name='contact_form'),
    path("faq", views.faqpage, name="faqpage"),
    path("job-update-page", views.job_update_page, name="job_update_page"),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('job/update/<int:job_id>/', views.update_job, name='update_job'),
    path("post-job", views.post_job, name="post_job"),
    path("post-jobs", views.post_jobs, name="post_jobs"),
    path("blog", views.blogpage, name="blogpage"),
    path("blog", views.blogpage, name="blogpage"),
    path('feedback-page', views.submit_feedback, name='feedback_page'),
    path('edit-profile-hr', views.edit_profile_hr, name='edit_profile_hr'),
    path("hr-dashboard", views.hr_dashboard, name="hr_dashboard"),
    path("candidate-dashboard", views.candidate_dashboard, name="candidate_dashboard"),
    path("available-jobs", views.available_jobs, name="available_jobs"),
    path("hr-register", views.hr_register_page, name="hr_register_page"),
    path("candidate-register", views.candidate_register_page, name="candidate_register_page"),
    path("hr-login-page", views.hr_login_page, name="hr_login_page"),
    path("candidate-login-page", views.candidate_login_page, name="candidate_login_page"),
    path("login-hr", views.hr_login, name="hr_login"),
    path("login-candidate", views.candidate_login, name="candidate_login"),
    path("", lambda request: redirect("JRS:startpage")),  # Use the app namespace and correct name
    path('register/hr/', views.hr_registration, name='register_hr'),
    path('register/candidate/', views.candidate_registration, name='register_candidate'),
    path("accounts/logout/", views.logout_user, name = "logout_user"),
    path("accounts/logouts/", views.logout_users, name = "logout_users"),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
