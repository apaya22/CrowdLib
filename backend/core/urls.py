# core/urls.py

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import redirect
from users.views import *
from madlibs.views import get_all_madlibs, get_madlib_by_id,search_madlibs

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
    path('', home_view),  
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('api/debug/oauth/', debug_oauth_data, name='debug-oauth'),
    # User API endpoints
    path('api/debug/oauth/', debug_oauth_data, name='debug-oauth'),
    path('api/users/', user_list, name='user-list'),
    path('api/users/current/', current_user_profile, name='current-user'),
    path('api/users/create/', create_user, name='create-user'),                    
    path('api/users/<str:user_id>/', user_detail, name='user-detail'),            
    path('api/users/<str:user_id>/update/', update_user, name='update-user'),     
    path('api/users/<str:user_id>/delete/', delete_user, name='delete-user'),    
    path('api/users/username/<str:username>/', user_by_username, name='user-by-username'),  

    # Madlib API endpoints
    path('api/madlibs/', get_all_madlibs, name='get_all_madlibs'),
    path('api/madlibs/<str:madlib_id>/', get_madlib_by_id, name='get_madlib_by_id'),
    path('api/madlibs/search/', search_madlibs, name='search_madlibs'),
]
