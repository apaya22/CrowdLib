# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from users.views import dashboard, debug_oauth_data, user_list, current_user_profile

urlpatterns = [
    path('', lambda request: redirect('/auth/login/google-oauth2/')),
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('dashboard/', dashboard, name='dashboard'),
    path('api/debug/oauth/', debug_oauth_data, name='debug-oauth'),
    path('api/users/', user_list, name='user-list'),
    path('api/users/current/', current_user_profile, name='current-user'),
    path('dashboard/', dashboard, name='dashboard'),  
    path('api/madlibs/', views.get_all_madlibs, name='get_all_madlibs'),
    path('api/madlibs/<str:madlib_id>/', views.get_madlib_by_id, name='get_madlib_by_id'),
    path('api/madlibs/search/', views.search_madlibs, name='search_madlibs'),
]

