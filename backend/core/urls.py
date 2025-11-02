# core/urls.py
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import redirect
from users.views import dashboard, debug_oauth_data, UserViewSet
from madlibs.views import MadLibTemplateViewSet, UserFilledMadlibsViewSet

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

urlpatterns = [
    path('api/', include(router.urls)),
    path('', lambda request: redirect('/auth/login/google-oauth2/')),
    path('', home_view),  
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('api/debug/oauth/', debug_oauth_data, name='debug-oauth'),
    # User API endpoints
    path('api/debug/oauth/', debug_oauth_data, name='debug-oauth'),
]
