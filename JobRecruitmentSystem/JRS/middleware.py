from django.contrib.auth.models import User
from django.shortcuts import redirect
from datetime import timedelta

class SuperUserSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            if request.user.is_superuser:
                # For superuser/admin, keep the session alive indefinitely
                request.session.set_expiry(0)  # Indefinite session expiry
                # Set a custom session cookie if needed
                response = self.get_response(request)
                response.set_cookie('admin_session', 'admin_session_value', max_age=None, expires=None)
            else:
                # For regular users, set session expiry to 1 hour (3600 seconds)
                request.session.set_expiry(3600)  # 1 hour expiry for regular users
                # Set a custom session cookie if needed
                response = self.get_response(request)
                response.set_cookie('user_session', 'user_session_value', max_age=None, expires=None)

            # Check if the session has expired (in case of inactivity for more than 1 hour)
            if request.session.get_expiry_age() <= 0:
                request.session.flush()  # Clear session data after expiry

        else:
            # If the user is not authenticated, process the request normally
            response = self.get_response(request)

        return response
