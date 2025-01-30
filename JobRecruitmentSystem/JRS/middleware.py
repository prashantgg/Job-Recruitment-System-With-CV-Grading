from django.http import HttpResponseRedirect
from django.urls import reverse

class SuperuserAdminMiddleware:
    """
    Middleware that ensures only superusers can access the admin panel.
    Non-superusers are redirected to the Django admin login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the path starts with '/admin/' and the user is not a superuser
        if request.path.startswith('/admin/'):

            # Check if the user is logged in and a superuser
            if not request.user.is_authenticated:
                # If not logged in, redirect to the default admin login page
                return HttpResponseRedirect(reverse('admin:login'))

            elif not request.user.is_superuser:
                # If the user is logged in but not a superuser, redirect to the default admin login page
                return HttpResponseRedirect(reverse('admin:login'))

        # Continue processing the request if it's an authorized user
        response = self.get_response(request)
        return response
