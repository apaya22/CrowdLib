# users/pipeline.py
from .models import UserOperations

def create_mongodb_user(strategy, details, backend, user=None, *args, **kwargs):
    if user and backend.name == 'google-oauth2':
        user_operator = UserOperations()
        # Extract data from Google
        response = kwargs.get('response', {})
        
        # Get Google user ID (not email)
        google_user_id = response.get('sub') 
        
        # Check if user already exists in MongoDB
        mongodb_user = user_operator.get_by_email(user.email)
        
        if not mongodb_user:
            # Create user in MongoDB with the correct Google ID
            try:
                user_id = user_operator.create(
                    username=user.username,
                    email=user.email,
                    oauth_provider='google',
                    oauth_id=google_user_id,
                    profile_picture=response.get('picture'),
                    bio=None
                )
                print(f"Created MongoDB user: {user_id}")
            except Exception as e:
                print(f"Error creating MongoDB user: {e}")
        else:
            print(f"User already exists in MongoDB: {mongodb_user['_id']}")
    
    return {'user': user}