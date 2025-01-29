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
    path("hr-register", views.hr_register_page, name="hr_register_page"),
    path("candidate-register", views.candidate_register_page, name="candidate_register_page"),
    path("login-page", views.login_page, name="login_page"),
    path("", lambda request: redirect("JRS:startpage")),  # Use the app namespace and correct name
]
