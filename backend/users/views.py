# users/views.py
from django.http import HttpResponse
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from .models import UserOperations

def dashboard(request):
    if request.user.is_authenticated:
        # Check MongoDB for this user
        user_operator = UserOperations()
        mongodb_user = user_operator.get_by_email(request.user.email)
        
        if mongodb_user:
            return HttpResponse(f"Welcome {request.user.email}! MongoDB User ID: {mongodb_user['_id']}")
        else:
            return HttpResponse(f"Welcome {request.user.email}! (Not yet in MongoDB)")
    else:
        return HttpResponse("Please log in.")

# Debug endpoint to see OAuth data
@api_view(['GET'])
def debug_oauth_data(request):
    user_operator = UserOperations()
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
        user_data['mongodb_user'] = user_operator.get_by_email(request.user.email)
            
        return Response(user_data)
    return Response({'error': 'Not authenticated'})

# API ENDPOINTS:

class UserViewSet(viewsets.ViewSet):
    """
    API endpoints for managing users.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserOperations()


    def get_permissions(self):
        """
        permission dictionary. Automatically called by rest_framework.permssions
        """
        permission_classes = {
            'list': [permissions.IsAdminUser],
            'create': [permissions.AllowAny],
            'retrieve': [permissions.AllowAny],
            'update': [permissions.IsAuthenticated],
            'destroy': [permissions.IsAuthenticated],
            'profile': [permissions.IsAuthenticated],
            'admin_stats': [permissions.IsAdminUser],
        }

        return [
            permission()
            for permission in permission_classes.get(self.action, [permissions.IsAdminUser])
        ]


    def list(self, request):
        """
        List all users with optional limit.

        Query Parameters:
        - limit: Maximum number of users to retrieve (default: 100)

        GET /api/users/?limit=50
        """
        try:
            limit = request.query_params.get('limit', 100)

            try:
                limit = int(limit)
                if limit <= 0:
                    limit = 100
            except ValueError:
                limit = 100

            users = self.user_service.get_all()

            return Response(
                {'count': len(users), 'results': users},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """
        Create a new user (public endpoint).

        Expected JSON:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "oauth_provider": "google",
            "oauth_id": "1234567890",
            "profile_picture": "https://...",
            "bio": "Hello, I'm John!"
        }
        """
        try:
            data = request.data

            required_fields = ['username', 'email', 'oauth_provider', 'oauth_id']
            if not all(field in data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields: {required_fields}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_id = self.user_service.create(
                username=data['username'],
                email=data['email'],
                oauth_provider=data['oauth_provider'],
                oauth_id=data['oauth_id'],
                profile_picture=data.get('profile_picture'),
                bio=data.get('bio')
            )

            return Response(
                {'user_id': user_id, 'message': 'User created successfully'},
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        Retrieve a user by ID (public endpoint).

        GET /api/users/{id}/
        """
        if not pk:
            return Response(
                {'error': 'Missing user ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = self.user_service.get_by_id(str(pk))

            if not user:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(user, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """
        Update a user's profile (authenticated only).

        Users can only update their own profile.

        Expected JSON (all fields optional):
        {
            "username": "new_username",
            "email": "newemail@example.com",
            "bio": "Updated bio",
            "profile_picture": "https://..."
        }
        """
        if not pk:
            return Response(
                {'error': 'Missing user ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is updating their own profile
        target_user = self.user_service.get_by_id(str(pk))
        if not target_user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_user = self.user_service.get_by_email(request.user.email)
        if not current_user or str(current_user['_id']) != str(pk):
            return Response(
                {'error': 'You can only update your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            data = request.data

            if not data:
                return Response(
                    {'error': 'No data provided for update'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = self.user_service.update_profile(str(pk), **data)

            if not success:
                return Response(
                    {'error': 'User not found or no valid fields to update'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {'message': 'User updated successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """
        Delete a user (authenticated only).

        Users can only delete their own account.

        DELETE /api/users/{id}/
        """
        if not pk:
            return Response(
                {'error': 'Missing user ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is deleting their own account
        current_user = self.user_service.get_by_email(request.user.email)
        if not current_user or str(current_user['_id']) != str(pk):
            return Response(
                {'error': 'You can only delete your own account'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            success = self.user_service.delete(str(pk))

            if not success:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {'message': 'User deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_username(self, request):
        """
        Get user by username (public endpoint).

        GET /api/users/by_username/?username=john_doe
        """
        try:
            username = request.query_params.get('username', '').strip()

            if not username:
                return Response(
                    {'error': 'username query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = self.user_service.get_by_username(username)

            if not user:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(user, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_email(self, request):
        """
        Get user by email (public endpoint).

        GET /api/users/by_email/?email=john@example.com
        """
        try:
            email = request.query_params.get('email', '').strip()

            if not email:
                return Response(
                    {'error': 'email query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = self.user_service.get_by_email(email)

            if not user:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(user, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Get current logged-in user's profile (authenticated only).

        GET /api/users/profile/
        """
        try:
            user = self.user_service.get_by_email(request.user.email)

            if not user:
                return Response(
                    {'error': 'User profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(user, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
