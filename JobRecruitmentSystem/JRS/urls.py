from django.shortcuts import redirect
from django.urls import path
from . import views
from . import cv_grading
from django.conf import settings
from django.conf.urls.static import static


app_name = "JRS"

urlpatterns = [
    path("home", views.startpage, name="startpage"),  # No space in the name
    path("about", views.aboutpage, name="aboutpage"),
    path('view-jobs/', views.view_jobs, name='view_jobs'),
    path('view-applications/', views.view_applications, name='view_applications'),
    path('job/<int:job_id>/', views.view_jobs, name='job_detail'),  # New path for job detail
    path('application/update/<int:application_id>/', views.update_application, name='update_application'),
    path("feature", views.featurepage, name="featurepage"),
    path("contact", views.contactpage, name="contactpage"),
    path('contact/', views.contact_form, name='contact_form'),
    path('jobs/<int:job_id>/', views.job_details, name='job_details'),
    path('job/detail/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job-listing', views.job_listing, name='job_listing'),
    path('change_password_candidate/', views.change_password_candidate, name='change_password_candidate'),
    path('change_password_hr/', views.change_password_hr, name='change_password_hr'),
    path("faq", views.faqpage, name="faqpage"),
    path("job-update-page", views.job_update_page, name="job_update_page"),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('delete-application/<int:application_id>/', views.delete_application, name='delete_application'),
    path('job/update/<int:job_id>/', views.update_job, name='update_job'),
    path("post-jobs", views.post_jobs, name="post_jobs"),
    path("blog", views.blogpage, name="blogpage"),
    path("blog", views.blogpage, name="blogpage"),
    path('feedback-page-hr', views.submit_feedback_hr, name='feedback_hr_page'),
    path('feedback-page-candidate', views.submit_feedback_candidate, name='feedback_candidate_page'),
    path('edit-profile-hr/', views.edit_hr_profile, name='edit_profile_hr'),
    path('edit-profile-candidate/', views.edit_candidate_profile, name='edit_profile_candidate'),
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
    path('apply-job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('jobs/', views.job_listing, name='job_listing'),
    path('jobs/search', views.list_job, name='list_job'),
    path('posted-jobs/', views.posted_jobs, name='posted_jobs'),
    path('job/<int:job_id>/view_applicants/', views.view_applicants, name='view_applicants'),
    path('application/<int:application_id>/cover_letter/', views.generate_cover_letter_pdf, name='generate_cover_letter_pdf'),
    path('grade-all-cvs/<int:job_id>/', cv_grading.grade_all_cvs, name='grade_all_cvs'),
    path('list/jobs/', views.job_list, name='list_job_hr'),
    path('job/<int:job_id>/graded-scores/', views.view_graded_scores, name='view_graded_scores'),
    path('job/application/<int:application_id>/accept/', views.accept_application, name='accept_application'),
    path('job/application/<int:application_id>/reject/', views.reject_application, name='reject_application'),
    path("my-jobs/", views.candidate_jobs, name="candidate_jobs"),
    path('schedule-interview/<int:job_id>/', views.schedule_interview, name='schedule_interview'),
    path('application-tracking/', views.application_tracking, name='application_tracking'),








]# This will allow Django to serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    