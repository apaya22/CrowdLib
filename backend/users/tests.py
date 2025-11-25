from django.test import TestCase
from users.models import UserOperations

class UserOperationsTest(TestCase):
    def setUp(self):
        """Set up test fixtures before each test"""
        self.user_operator = UserOperations()
        # Track created users for cleanup
        self.created_user_ids = []

        # Clean up any leftover test data from previous runs
        test_usernames = ['john_doe', 'bob_smith', 'temp_user', 'unique_user']
        for username in test_usernames:
            try:
                self.user_operator.delete_by_username(username)
            except Exception:
                pass

    def tearDown(self):
        """Clean up after each test"""
        # Delete all users created during the test
        for user_id in self.created_user_ids:
            try:
                self.user_operator.delete(user_id)
            except Exception:
                pass  # Ignore errors if user was already deleted

        # Also clean up by username to catch any that might have been created but not tracked
        test_usernames = ['john_doe', 'bob_smith', 'temp_user', 'unique_user']
        for username in test_usernames:
            try:
                self.user_operator.delete_by_username(username)
            except Exception:
                pass

    def test_create_user(self):
        """Test creating a new user"""
        user_id = self.user_operator.create(
            username='john_doe',
            email='john@example.com',
            oauth_provider='google',
            oauth_id='google_123456',
            bio='Software developer'
        )
        self.created_user_ids.append(user_id)
        self.assertIsNotNone(user_id)
        user_check = self.user_operator.get_by_id(user_id)
        self.assertIsNotNone(user_check)
        self.assertEqual(user_check['email'],"john@example.com") # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user_check['username'],"john_doe")      # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user_check['bio'],"Software developer") # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user_check['oauth_provider'],"google")  # pyright: ignore[reportOptionalSubscript]
        
        


    def test_update_profile(self):
        user_id = self.user_operator.create(
            username='bob_smith',
            email='bob@example.com',
            oauth_provider='google',
            oauth_id='google_345678'
        )
        self.created_user_ids.append(user_id)

        # Update profile
        success = self.user_operator.update_profile(
            user_id,
            bio='Updated bio',
            profile_picture='https://s3.example.com/bob.jpg'
        )

        self.assertTrue(success)
        user = self.user_operator.get_by_id(user_id)

        self.assertIsNotNone(user)
        self.assertEqual(user['bio'], 'Updated bio') # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(user['profile_picture'], 'https://s3.example.com/bob.jpg') # pyright: ignore[reportOptionalSubscript]
        
        
    def test_delete_user(self):
        """Test deleting a user"""
        user_id = self.user_operator.create(
            username='temp_user',
            email='temp@example.com',
            oauth_provider='github',
            oauth_id='github_111222'
        )
        self.created_user_ids.append(user_id)

        # Delete user
        success = self.user_operator.delete(user_id)
        self.assertTrue(success)

        # Verify deletion
        user = self.user_operator.get_by_id(user_id)
        self.assertIsNone(user)

    def test_duplicate_username(self):
        """Test that duplicate usernames are rejected"""
        user_id = self.user_operator.create(
            username='unique_user',
            email='user1@example.com',
            oauth_provider='google',
            oauth_id='google_555666'
        )
        self.created_user_ids.append(user_id)

        # Try to create another with same username
        with self.assertRaises(ValueError):
            self.user_operator.create(
                username='unique_user',
                email='user2@example.com',
                oauth_provider='github',
                oauth_id='github_777888'
            )
