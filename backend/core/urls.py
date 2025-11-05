# core/urls.py
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import redirect
from users.views import dashboard, debug_oauth_data, UserViewSet
from madlibs.views import MadLibTemplateViewSet, UserFilledMadlibsViewSet
from django.conf import settings

router = DefaultRouter()
router.register(r'madlibs', UserFilledMadlibsViewSet, basename='madlib')
router.register(r'templates', MadLibTemplateViewSet, basename='template')
router.register(r'users', UserViewSet, basename='user')


#home view for backend server, lists available endpoints
def home_view(request):
    return JsonResponse({
        "message": "CrowdLib API Backend",
        "endpoints": [
            "/auth/login/google-oauth2/",
            "/api/users/",
            "/api/madlibs/",
        ]
    })

#Added 11/1
# Redirect backend hit to the frontend route
def oauth_complete_signup_redirect(request):
    # If you have a setting, use that; otherwise hardcode your dev URL
    origin = getattr(settings, "FRONTEND_ORIGIN", "http://localhost:5173")
    return redirect(f"{origin}/oauth-complete-signup")

urlpatterns = [
    path('api/', include(router.urls)),
    path('', lambda request: redirect('/auth/login/google-oauth2/')),
    path('', home_view),  
    path('admin/', admin.site.urls),
    # added complete_signup redirect
    path('oauth-complete-signup', oauth_complete_signup_redirect, name='oauth-complete-signup'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('api/debug/oauth/', debug_oauth_data, name='debug-oauth'),
    # User API endpoints
    path('api/debug/oauth/', debug_oauth_data, name='debug-oauth'),
]
