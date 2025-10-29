# users/views.py
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserOperations


# Debug endpoint to see OAuth data
@api_view(['GET'])
def debug_oauth_data(request):
    if request.user.is_authenticated:
        user_data = {
            'django_user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            },
            'social_auth': [],
            'mongodb_user': None
        }
        
        # Get Google OAuth data
        social_accounts = request.user.social_auth.all()
        for social in social_accounts:
            user_data['social_auth'].append({
                'provider': social.provider,
                'uid': social.uid,
                'extra_data': social.extra_data
            })
        
        # Get MongoDB user data
        user_data['mongodb_user'] = UserOperations.get_by_email(request.user.email)
            
        return Response(user_data)
    return Response({'error': 'Not authenticated'})

# API ENDPOINTS:

@api_view(['GET'])
def user_list(request):
    """Get all users"""
    try:
        users = UserOperations.get_all()
        return Response(users)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def user_detail(request, user_id):
    """Get specific user by ID"""
    try:
        user = UserOperations.get_by_id(user_id)
        if user:
            return Response(user)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def user_by_username(request, username):
    """Get user by username"""
    try:
        user = UserOperations.get_by_username(username)
        if user:
            return Response(user)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_user(request):
    """Create a new user"""
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['username', 'email', 'oauth_provider', 'oauth_id']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'Missing required field: {field}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        user_id = UserOperations.create(
            username=data['username'],
            email=data['email'],
            oauth_provider=data['oauth_provider'],
            oauth_id=data['oauth_id'],
            profile_picture=data.get('profile_picture'),
            bio=data.get('bio')
        )
        return Response({'user_id': user_id, 'message': 'User created successfully'}, 
                       status=status.HTTP_201_CREATED)
    
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_user(request, user_id):
    """Update user profile"""
    try:
        data = request.data
        
        # Only allow certain fields to be updated
        allowed_fields = {'bio', 'profile_picture', 'username', 'email'}
        update_data = {key: value for key, value in data.items() if key in allowed_fields}
        
        if not update_data:
            return Response({'error': 'No valid fields to update'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        result = UserOperations.update_profile(user_id, **update_data)
        if result:
            return Response({'message': ' User updated successfully'})
        return Response({'error': ' User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_user(request, user_id):
    """Delete a user"""
    try:
        success = UserOperations.delete(user_id)
        if success:
            return Response({'message': 'User deleted successfully'})
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def current_user_profile(request):
    """Get current logged-in user's profile"""
    if request.user.is_authenticated:
        try:
            user = UserOperations.get_by_email(request.user.email)
            if user:
                return Response(user)
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)