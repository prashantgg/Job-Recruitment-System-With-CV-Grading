# middleware.py
from django.shortcuts import redirect
from django.contrib.auth.models import User

class SuperUserSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            request.session.set_expiry(0)  # Keep the superuser session alive

        response = self.get_response(request)
        return response
