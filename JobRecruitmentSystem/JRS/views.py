from django.http import HttpResponse
from django.shortcuts import render

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

