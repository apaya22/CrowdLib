from django.http import HttpResponse

def dashboard(request):
    if request.user.is_authenticated:
        return HttpResponse(f"Welcome {request.user.email}! You're logged in.")
    else:
        return HttpResponse("Please log in.")
