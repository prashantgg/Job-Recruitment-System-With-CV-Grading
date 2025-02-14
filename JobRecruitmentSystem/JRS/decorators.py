from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def hr_required(view_func):
    """Allow only HR users to access the view."""
    def wrapper(request, *args, **kwargs):
        print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}, Groups: {request.user.groups.all()}")
        if not request.user.is_authenticated or not request.user.groups.filter(name='HR').exists():
            return HttpResponseForbidden("Access Denied: HRs only")
        return view_func(request, *args, **kwargs)
    return wrapper

def candidate_required(view_func):
    """Allow only Candidate users to access the view."""
    def wrapper(request, *args, **kwargs):
        print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}, Groups: {request.user.groups.all()}")
        if not request.user.is_authenticated or not request.user.groups.filter(name='Candidate').exists():
            return HttpResponseForbidden("Access Denied: Candidates only")
        return view_func(request, *args, **kwargs)
    return wrapper
