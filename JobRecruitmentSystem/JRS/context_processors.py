from .models import HR, Candidate

def hr_profile(request):
    """Context processor to add HR profile data to all templates."""
    hr = None
    if request.user.is_authenticated:
        try:
            hr = HR.objects.get(user=request.user)
        except HR.DoesNotExist:
            pass
    return {'hr': hr}
def candidate_profile(request):
    """Context processor to add HR profile data to all templates."""
    candidate = None
    if request.user.is_authenticated:
        try:
            candidate = Candidate.objects.get(user=request.user)
        except Candidate.DoesNotExist:
            pass
    return {'candidate': candidate}
