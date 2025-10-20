from django.test import TestCase
from api.mongo_operations import UserOperations

class UserOperationsTest(TestCase):
    def test_create_user(self):
        """Test creating a new user with OAuth"""
        UserOperations._try_delete_user('john_doe')
        user_id = UserOperations.create(
            username='john_doe',
            email='john@example.com',
            oauth_provider='google',
            oauth_id='google_123456',
            bio='Software developer'
        )

        self.assertIsNotNone(user_id)


    def test_update_profile(self):
        
        UserOperations._try_delete_user("bob_smith")
        user_id = UserOperations.create(
            username='bob_smith',
            email='bob@example.com',
            oauth_provider='google',
            oauth_id='google_345678'
        )

        # Update profile
        success = UserOperations.update_profile(
            user_id,
            bio='Updated bio',
            profile_picture='https://s3.example.com/bob.jpg'
        )

        self.assertTrue(success)
        user = UserOperations.get_by_id(user_id)
        
        self.assertIsNotNone(user)
        self.assertEqual(user['bio'], 'Updated bio')
        self.assertEqual(user['profile_picture'], 'https://s3.example.com/bob.jpg')
        
        
    def test_delete_user(self):
        """Test deleting a user"""
        UserOperations._try_delete_user('temp_user')
        user_id = UserOperations.create(
            username='temp_user',
            email='temp@example.com',
            oauth_provider='github',
            oauth_id='github_111222'
        )

        # Delete user
        success = UserOperations.delete(user_id)
        self.assertTrue(success)

        # Verify deletion
        user = UserOperations.get_by_id(user_id)
        self.assertIsNone(user)

    def test_duplicate_username(self):
        """Test that duplicate usernames are rejected"""
        UserOperations._try_delete_user('unique_user')
        UserOperations.create(
            username='unique_user',
            email='user1@example.com',
            oauth_provider='google',
            oauth_id='google_555666'
        )

        # Try to create another with same username
        with self.assertRaises(ValueError):
            UserOperations.create(
                username='unique_user',
                email='user2@example.com',
                oauth_provider='github',
                oauth_id='github_777888'
            )
