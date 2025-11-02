from django.test import TestCase
from users.models import UserOperations

class UserOperationsTest(TestCase):
    def test_create_user(self):
        """Test creating a new user with OAuth"""
        user_operator = UserOperations()
        user_id = user_operator.create(
            username='john_doe',
            email='john@example.com',
            oauth_provider='google',
            oauth_id='google_123456',
            bio='Software developer'
        )
        self.assertIsNotNone(user_id)
        user_check = user_operator.get_by_id(user_id)
        self.assertIsNotNone(user_check)
        self.assertEqual(user_check['email'],"john@example.com") # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user_check['username'],"john_doe")      # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user_check['bio'],"Software developer") # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user_check['oauth_provider'],"google")  # pyright: ignore[reportOptionalSubscript]
        
        


    def test_update_profile(self):
        user_operator = UserOperations()
        user_id = user_operator.create(
            username='bob_smith',
            email='bob@example.com',
            oauth_provider='google',
            oauth_id='google_345678'
        )

        # Update profile
        success = user_operator.update_profile(
            user_id,
            bio='Updated bio',
            profile_picture='https://s3.example.com/bob.jpg'
        )

        self.assertTrue(success)
        user = user_operator.get_by_id(user_id)
        
        self.assertIsNotNone(user)
        self.assertEqual(user['bio'], 'Updated bio') # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user['profile_picture'], 'https://s3.example.com/bob.jpg') # pyright: ignore[reportOptionalSubscript]
        
        
    def test_delete_user(self):
        """Test deleting a user"""
        user_operator = UserOperations()
        user_id = user_operator.create(
            username='temp_user',
            email='temp@example.com',
            oauth_provider='github',
            oauth_id='github_111222'
        )

        # Delete user
        success = user_operator.delete(user_id)
        self.assertTrue(success)

        # Verify deletion
        user = user_operator.get_by_id(user_id)
        self.assertIsNone(user)

    def test_duplicate_username(self):
        """Test that duplicate usernames are rejected"""
        user_operator = UserOperations()
        user_operator.create(
            username='unique_user',
            email='user1@example.com',
            oauth_provider='google',
            oauth_id='google_555666'
        )

        # Try to create another with same username
        with self.assertRaises(ValueError):
            user_operator.create(
                username='unique_user',
                email='user2@example.com',
                oauth_provider='github',
                oauth_id='github_777888'
            )
