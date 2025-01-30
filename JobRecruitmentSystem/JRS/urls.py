from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = "JRS"

urlpatterns = [
    path("home", views.startpage, name="startpage"),  # No space in the name
    path("about", views.aboutpage, name="aboutpage"),
    path("feature", views.featurepage, name="featurepage"),
    path("contact", views.contactpage, name="contactpage"),
    path('contact/', views.contact_form, name='contact_form'),
    path("faq", views.faqpage, name="faqpage"),
    path("blog", views.blogpage, name="blogpage"),
    path("hr-dashboard", views.hr_dashboard, name="hr_dashboard"),
    path("candidate-dashboard", views.candidate_dashboard, name="candidate_dashboard"),
    path("hr-register", views.hr_register_page, name="hr_register_page"),
    path("candidate-register", views.candidate_register_page, name="candidate_register_page"),
    path("hr-login-page", views.hr_login_page, name="hr_login_page"),
    path("candidate-login-page", views.candidate_login_page, name="candidate_login_page"),
    path("login-hr", views.hr_login, name="hr_login"),
    path("login-candidate", views.candidate_login, name="candidate_login"),
    path("", lambda request: redirect("JRS:startpage")),  # Use the app namespace and correct name
    path('register/hr/', views.hr_registration, name='register_hr'),
    path('register/candidate/', views.candidate_registration, name='register_candidate'),
]
