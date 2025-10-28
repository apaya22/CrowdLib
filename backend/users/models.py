from core.db_connect import get_collection
from datetime import datetime, timezone
from bson.objectid import ObjectId


#Database User Operation Model
class UserOperations:
    @staticmethod
    def create(username, email, oauth_provider, oauth_id, profile_picture=None, bio=None) -> str:
        """
        Create a new user

        Args:
            username: Unique username
            email: Unique email address
            oauth_provider: OAuth provider ('google', 'github', etc.)
            oauth_id: OAuth ID from the provider
            profile_picture: Optional S3 URL
            bio: Optional user bio
            public: bool
            banned: bool

        Returns:
            str: User ID (ObjectId as string)
        """
        users_collection = get_collection('users')

        # Check if user already exists
        if users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
            raise ValueError("Username or email already exists")

        now = datetime.now(timezone.utc)
        
        user_data = {
            'username': username,
            'email': email,
            'oauth_provider': oauth_provider,
            'oauth_id': oauth_id,
            'profile_picture': profile_picture,
            'bio': bio,
            'created_at': now,
            'updated_at': now,
            'public': True,
            'banned': False,
            'followers_count': 0,
            'following_count': 0
        }

        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    

    @staticmethod
    def get_by_id(user_id):
        """Get user by ObjectId"""
        users_collection = get_collection('users')
        user = users_collection.find_one({'_id': ObjectId(user_id)})

        if user:
            user['_id'] = str(user['_id'])

        return user

    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        users_collection = get_collection('users')
        user = users_collection.find_one({'username': username})

        if user:
            user['_id'] = str(user['_id'])

        return user


    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        users_collection = get_collection('users')
        user = users_collection.find_one({'email': email})

        if user: user['_id'] = str(user['_id'])

        return user

    @staticmethod
    def update_profile(user_id, **kwargs):
        """
        Update user profile information

        Args:
            user_id: User ObjectId as string
            **kwargs: Fields to update (bio, profile_picture, username, email)

        Returns:
            bool: True if update was successful
        """
        users_collection = get_collection('users')

        # Fields that can be updated
        allowed_fields = {'bio', 'profile_picture', 'username', 'email'}
        update_data = {key: value for key, value in kwargs.items() if key in allowed_fields}

        # Always update the updated_at timestamp
        update_data['updated_at'] = datetime.now(timezone.utc)

        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result

    @staticmethod
    def delete(user_id):
        """
        Delete a user

        Args:
            user_id: User ObjectId as string

        Returns:
            bool: True if deletion was successful
        """
        users_collection = get_collection('users')
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0

    @staticmethod
    def _try_delete_user(username):
        """
        For testing
        Delete a user if they exist, otherwise returns None
        
        Args:
            user_id: User ObjectId as string

        Returns:
            bool/None: 
                    True if user exists and deletion was successful
                    
                    False if user exists but the deletion failed
                    
                    None if the user does not exist
        """
        users_collection = get_collection('users')
        try:
            result = users_collection.delete_one({'username': username})
        except:
            return None
        return result.deleted_count > 0
        
    @staticmethod
    def get_all():
        """Get all users (max 100)"""
        users_collection = get_collection('users')
        users = list(users_collection.find().limit(100))

        for user in users:
            user['_id'] = str(user['_id'])

        return users



