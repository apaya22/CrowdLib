from core.db_connect import get_collection
from datetime import datetime, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId


class UserOperations:
    def __init__(self):
        self.collection = get_collection('users')

    def create(self, username: str, email: str, oauth_provider: str, oauth_id: str, 
               profile_picture = None, bio = None) -> str:
        """
        Create a new user

        Args:
            username: Unique username
            email: Unique email address
            oauth_provider: OAuth provider ('google', 'github', etc.)
            oauth_id: OAuth ID from the provider
            profile_picture: Optional S3 URL
            bio: Optional user bio

        Returns:
            str: User ID (ObjectId as string)

        Raises:
            ValueError: If username or email already exists
        """
        # Check if user already exists
        if self.collection.find_one({'$or': [{'username': username}, {'email': email}]}):
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

        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def get_by_id(self, user_id: str):
        """
        Get user by ObjectId

        Args:
            user_id: User ObjectId as string

        Returns:
            Dictionary containing user data or None if not found
        """
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except InvalidId:
            return None

    def get_by_username(self, username: str):
        """
        Get user by username

        Args:
            username: Username to search for

        Returns:
            Dictionary containing user data or None if not found
        """
        try:
            user = self.collection.find_one({'username': username})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            print(f"Error retrieving user by username: {e}")
            return None

    def get_by_email(self, email: str):
        """
        Get user by email

        Args:
            email: Email to search for

        Returns:
            Dictionary containing user data or None if not found
        """
        try:
            user = self.collection.find_one({'email': email})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            return None

    def update_profile(self, user_id: str, **kwargs) -> bool:
        """
        Update user profile information

        Args:
            user_id: User ObjectId as string
            **kwargs: Fields to update (bio, profile_picture, username, email)

        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Fields that can be updated
            allowed_fields = {'bio', 'profile_picture', 'username', 'email'}
            update_data = {key: value for key, value in kwargs.items() if key in allowed_fields}

            if not update_data:
                return False

            # Always update the updated_at timestamp
            update_data['updated_at'] = datetime.now(timezone.utc)

            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except InvalidId:
            return False
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False

    def delete(self, user_id: str) -> bool:
        """
        Delete a user

        Args:
            user_id: User ObjectId as string

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except InvalidId:
            return False
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def delete_by_username(self, username: str) -> bool:
        """
        Delete a user by username (for testing)

        Args:
            username: Username of user to delete

        Returns:
            bool: True if user existed and was deleted, False otherwise
        """
        try:
            result = self.collection.delete_one({'username': username})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user by username: {e}")
            return False

    def get_all(self, limit: int = 100) -> list:
        """
        Get all users

        Args:
            limit: Maximum number of users to retrieve (default: 100)

        Returns:
            List of users
        """
        try:
            users = list(self.collection.find().limit(limit))
            for user in users:
                user['_id'] = str(user['_id'])
            return users
        except Exception as e:
            print(f"Error retrieving all users: {e}")
            return []
