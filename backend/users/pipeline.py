# users/pipeline.py
from .models import UserOperations

def create_mongodb_user(strategy, details, backend, response, *args, **kwargs):
    user_operator = UserOperations()
    """Create MongoDB user BEFORE Django user is created"""
    if backend.name == 'google-oauth2':
        # Get data directly from Google response
        email = response.get('email')
        google_user_id = response.get('sub')
        username = details.get('username', email.split('@')[0])
        profile_picture = response.get('picture')
        
        print(f"PIPELINE: Processing email '{email}'")
        print(f"PIPELINE: Google ID: {google_user_id}")
        
        # Check if user already exists in MongoDB
        mongodb_user = user_operator.get_by_email(email)
        
        if not mongodb_user:
            print(f"PIPELINE: Creating NEW MongoDB user: {email}")
            try:
                user_id = user_operator.create(
                    username=username,
                    email=email,
                    oauth_provider='google',
                    oauth_id=google_user_id,
                    profile_picture=profile_picture,
                    bio=None
                )
                print(f"PIPELINE: Created MongoDB user: {user_id}")
            except Exception as e:
                print(f"PIPELINE: Error creating user: {e}")
        else:
            print(f"PIPELINE: User already exists: {mongodb_user['_id']}")
    
    # Return the data for the next pipeline step
    return {
        'username': details.get('username'),
        'email': response.get('email'),
        'first_name': details.get('first_name'),
        'last_name': details.get('last_name'),
    }