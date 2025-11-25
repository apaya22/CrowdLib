from core.db_connect import get_collection
from datetime import datetime, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)


class UserOperations:
    def __init__(self):
        self.collection = get_collection('users')
        self._create_indexes()

    def _create_indexes(self):
        """
        Create database indexes for efficient user queries.
        Called automatically during initialization.
        """
        try:
            logger.debug("Creating user indexes")

            # Email lookups 
            self.collection.create_index([("email", 1)], unique=True, name="idx_email_unique")

            # Username lookups
            self.collection.create_index([("username", 1)], unique=True, name="idx_username_unique")

            # OAuth provider + ID
            self.collection.create_index([("oauth_provider", 1), ("oauth_id", 1)],
                                         unique=True, name="idx_oauth_unique")

            logger.info("User indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating user indexes: {e}")

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
        logger.debug(f"Creating new user: username={username}, email={email}, provider={oauth_provider}")

        # Check if user already exists
        if self.collection.find_one({'$or': [{'username': username}, {'email': email}]}):
            logger.warning(f"User creation failed - username or email already exists: {username}, {email}")
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

        try:
            result = self.collection.insert_one(user_data)
            logger.info(f"User created: {result.inserted_id} ({username})")
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            # Handle race condition where user was created between check and insert
            logger.warning(f"User creation failed - duplicate key error: {username}, {email}")
            # Determine which field caused the duplicate
            error_msg = str(e)
            if 'username' in error_msg:
                raise ValueError("Username already exists")
            elif 'email' in error_msg:
                raise ValueError("Email already exists")
            elif 'oauth' in error_msg:
                raise ValueError("OAuth account already linked to another user")
            else:
                raise ValueError("User already exists")

    def get_by_id(self, user_id: str):
        """
        Get user by ObjectId

        Args:
            user_id: User ObjectId as string

        Returns:
            Dictionary containing user data or None if not found
        """
        try:
            logger.debug(f"Retrieving user by ID: {user_id}")
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                logger.info(f"User found: {user_id} ({user.get('username', 'N/A')})")
            else:
                logger.info(f"User not found: {user_id}")
            return user
        except InvalidId:
            logger.warning(f"Invalid user ID format: {user_id}")
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
            logger.debug(f"Retrieving user by username: {username}")
            user = self.collection.find_one({'username': username})
            if user:
                user['_id'] = str(user['_id'])
                logger.info(f"User found by username: {username}")
            else:
                logger.info(f"User not found by username: {username}")
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
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
            logger.debug(f"Retrieving user by email: {email}")
            user = self.collection.find_one({'email': email})
            if user:
                user['_id'] = str(user['_id'])
                logger.info(f"User found by email: {email}")
            else:
                logger.info(f"User not found by email: {email}")
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
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
            logger.debug(f"Updating user profile: {user_id}, fields={list(kwargs.keys())}")
            # Fields that can be updated
            allowed_fields = {'bio', 'profile_picture', 'username', 'email'}
            update_data = {key: value for key, value in kwargs.items() if key in allowed_fields}

            if not update_data:
                logger.info(f"No valid fields to update for user: {user_id}")
                return False

            # Always update the updated_at timestamp
            update_data['updated_at'] = datetime.now(timezone.utc)

            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            if result.modified_count > 0:
                logger.info(f"User profile updated: {user_id}")
            else:
                logger.info(f"No changes made to user profile: {user_id}")
            return result.modified_count > 0
        except InvalidId:
            logger.warning(f"Invalid user ID format: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
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
            logger.debug(f"Deleting user: {user_id}")
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            if result.deleted_count > 0:
                logger.info(f"User deleted: {user_id}")
            else:
                logger.info(f"User not found: {user_id}")
            return result.deleted_count > 0
        except InvalidId:
            logger.warning(f"Invalid user ID format: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
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
            logger.debug(f"Deleting user by username: {username}")
            result = self.collection.delete_one({'username': username})
            if result.deleted_count > 0:
                logger.info(f"User deleted by username: {username}")
            else:
                logger.info(f"User not found by username: {username}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user by username {username}: {e}")
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
            logger.debug(f"Retrieving all users (limit={limit})")
            users = list(self.collection.find().limit(limit))
            for user in users:
                user['_id'] = str(user['_id'])
            logger.info(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Error retrieving all users: {e}")
            return []
