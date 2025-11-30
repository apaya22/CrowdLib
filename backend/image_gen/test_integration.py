#NOTICE: This file is primarily AI generated

"""
Integration tests for image generation workflow.

These tests verify the actual integration between components without extensive mocking.
Run with: python manage.py test image_gen.test_integration

Note: These tests require:
- MongoDB running and accessible
- Valid GEMINI_API_KEY in settings
- Valid AWS credentials and S3 bucket configured
"""

from django.test import TestCase
from madlibs.models import UserFilledMadlibs, MadLibTemplate
from users.models import UserOperations
from image_gen.models import ImageGenerationModel
import os


class ImageGenerationIntegrationTest(TestCase):
    """
    Integration tests for the full image generation workflow.

    These tests use real services and should only be run when:
    1. You have valid API credentials
    2. You want to test the actual integration
    3. You're okay with API costs (small)

    To run: python manage.py test image_gen.test_integration.ImageGenerationIntegrationTest --settings=core.settings
    """

    @classmethod
    def setUpClass(cls):
        """Check if integration tests should run"""
        super().setUpClass()
        cls.skip_integration = os.getenv('SKIP_INTEGRATION_TESTS', 'true').lower() == 'true'

        if cls.skip_integration:
            print("\n" + "="*70)
            print("SKIPPING INTEGRATION TESTS")
            print("Set SKIP_INTEGRATION_TESTS=false to run these tests")
            print("Warning: This will make real API calls and incur costs")
            print("="*70 + "\n")

    def setUp(self):
        """Set up test fixtures"""
        if self.skip_integration:
            self.skipTest("Integration tests disabled. Set SKIP_INTEGRATION_TESTS=false to enable.")

        self.template_service = MadLibTemplate()
        self.madlib_service = UserFilledMadlibs()
        self.user_service = UserOperations()

        # Create test template
        self.template_id = self.template_service.create({
            'title': 'Integration Test Template',
            'story': 'Once upon a time there was a {adjective} {noun}',
            'blanks': [
                {'id': '1', 'placeholder': 'adjective', 'type': 'adjective'},
                {'id': '2', 'placeholder': 'noun', 'type': 'noun'}
            ]
        })
        assert self.template_id is not None, "Failed to create test template"  # type: ignore[assert-type]

        # Create test user
        self.creator_id = self.user_service.create(
            username='integration_test_user',
            email='integration@test.com',
            oauth_provider='google',
            oauth_id='integration_test_123'
        )
        assert self.creator_id is not None, "Failed to create test user"  # type: ignore[assert-type]

        # Create test madlib
        self.madlib_id = self.madlib_service.new_filled_madlib(
            template_id=self.template_id,
            creator_id=self.creator_id,
            inputted_blanks=[
                {"id": "1", "input": "magical"},
                {"id": "2", "input": "unicorn"}
            ]
        )
        assert self.madlib_id is not None, "Failed to create test madlib"  # type: ignore[assert-type]

    def tearDown(self):
        """Clean up test data"""
        if hasattr(self, 'madlib_id') and self.madlib_id:
            self.madlib_service.delete_filled_madlib(self.madlib_id)
        if hasattr(self, 'template_id') and self.template_id:
            self.template_service.delete(self.template_id)
        if hasattr(self, 'creator_id') and self.creator_id:
            self.user_service.delete(self.creator_id)

    def test_full_image_generation_workflow(self):
        """
        Test the complete image generation workflow:
        1. Generate image with Gemini API
        2. Upload to S3
        3. Update madlib with image URL
        4. Verify madlib has image_url field

        WARNING: This test makes real API calls and will incur costs!
        """
        print("\n" + "="*70)
        print("RUNNING FULL INTEGRATION TEST")
        print("This will make real API calls to Gemini and AWS S3")
        print("="*70 + "\n")

        # Initialize the image generation model
        image_gen = ImageGenerationModel()

        # Generate image with a simple prompt
        madlib_text = "A magical unicorn in a enchanted forest"

        print(f"Generating image for: {madlib_text}")
        image_url = image_gen.create_image(
            madlib_text=madlib_text,
            madlib_id=self.madlib_id,  # type: ignore[arg-type]
            extra_prompt_args={
                'style': 'watercolor painting',
                'aspect_ratio': '1:1',
            }
        )

        # Verify image URL was generated
        self.assertIsNotNone(image_url, "Image URL should not be None")
        assert image_url is not None  # type: ignore[assert-type]
        self.assertTrue(image_url.startswith('http'), "Image URL should be a valid URL")
        print(f"✓ Generated image URL: {image_url}")

        # Update madlib with the image URL
        success = self.madlib_service.update_image_url(self.madlib_id, image_url)  # type: ignore[arg-type]
        self.assertTrue(success, "Madlib update should succeed")
        print(f"✓ Updated madlib with image URL")

        # Verify the madlib was updated
        updated_madlib = self.madlib_service.get_by_id(self.madlib_id)  # type: ignore[arg-type]
        self.assertIsNotNone(updated_madlib)
        assert updated_madlib is not None  # type: ignore[assert-type]
        self.assertIn('image_url', updated_madlib)
        self.assertEqual(updated_madlib['image_url'], image_url)
        print(f"✓ Verified madlib has correct image_url")

        print("\n" + "="*70)
        print("INTEGRATION TEST PASSED!")
        print(f"Image URL: {image_url}")
        print("="*70 + "\n")

    def test_image_generation_with_different_styles(self):
        """
        Test image generation with different style parameters.

        WARNING: This test makes real API calls and will incur costs!
        """
        if self.skip_integration:
            self.skipTest("Integration tests disabled")

        print("\n" + "="*70)
        print("TESTING DIFFERENT IMAGE STYLES")
        print("="*70 + "\n")

        image_gen = ImageGenerationModel()
        madlib_text = "A peaceful sunset over the ocean"

        styles = [
            {'style': 'photorealistic', 'aspect_ratio': '16:9'},
            {'style': 'anime', 'aspect_ratio': '4:3'},
        ]

        for idx, style_args in enumerate(styles):
            print(f"\nTest {idx + 1}: {style_args}")

            image_url = image_gen.create_image(
                madlib_text=madlib_text,
                madlib_id=f"test_{idx}_{self.madlib_id}",
                extra_prompt_args=style_args
            )

            if image_url:
                print(f"  ✓ Generated: {image_url}")
                self.assertTrue(image_url.startswith('http'))
            else:
                print(f"  ✗ Failed to generate image")
                self.fail(f"Failed to generate image for style: {style_args}")

        print("\n" + "="*70)
        print("STYLE TEST COMPLETED")
        print("="*70 + "\n")


class DatabaseIntegrationTest(TestCase):
    """
    Test database operations without external API calls.
    These tests are safe to run anytime.
    """

    def setUp(self):
        """Set up test fixtures"""
        self.template_service = MadLibTemplate()
        self.madlib_service = UserFilledMadlibs()
        self.user_service = UserOperations()

        # Create test template
        self.template_id = self.template_service.create({
            'title': 'DB Test Template',
            'story': 'Test story',
            'blanks': []
        })
        assert self.template_id is not None, "Failed to create test template"  # type: ignore[assert-type]

        # Create test user
        self.creator_id = self.user_service.create(
            username='db_test_user',
            email='db_test@test.com',
            oauth_provider='google',
            oauth_id='db_test_123'
        )
        assert self.creator_id is not None, "Failed to create test user"  # type: ignore[assert-type]

        # Create test madlib
        self.madlib_id = self.madlib_service.new_filled_madlib(
            template_id=self.template_id,
            creator_id=self.creator_id,
            inputted_blanks=[{"id": "1", "input": "test"}]
        )
        assert self.madlib_id is not None, "Failed to create test madlib"  # type: ignore[assert-type]

    def tearDown(self):
        """Clean up test data"""
        if hasattr(self, 'madlib_id') and self.madlib_id:
            self.madlib_service.delete_filled_madlib(self.madlib_id)
        if hasattr(self, 'template_id') and self.template_id:
            self.template_service.delete(self.template_id)
        if hasattr(self, 'creator_id') and self.creator_id:
            self.user_service.delete(self.creator_id)

    def test_madlib_image_url_update_workflow(self):
        """Test the database update workflow for image URLs"""
        # Initial state - no image_url
        madlib = self.madlib_service.get_by_id(self.madlib_id)  # type: ignore[arg-type]
        assert madlib is not None  # type: ignore[assert-type]
        self.assertNotIn('image_url', madlib)

        # Update with image URL
        test_url = "https://s3.example.com/test_image.png"
        success = self.madlib_service.update_image_url(self.madlib_id, test_url)  # type: ignore[arg-type]
        self.assertTrue(success)

        # Verify update
        updated_madlib = self.madlib_service.get_by_id(self.madlib_id)  # type: ignore[arg-type]
        assert updated_madlib is not None  # type: ignore[assert-type]
        self.assertEqual(updated_madlib['image_url'], test_url)
        self.assertIn('updated_at', updated_madlib)

        # Update with new URL
        new_url = "https://s3.example.com/new_image.png"
        success = self.madlib_service.update_image_url(self.madlib_id, new_url)  # type: ignore[arg-type]
        self.assertTrue(success)

        # Verify new update
        final_madlib = self.madlib_service.get_by_id(self.madlib_id)  # type: ignore[arg-type]
        assert final_madlib is not None  # type: ignore[assert-type]
        self.assertEqual(final_madlib['image_url'], new_url)

    def test_concurrent_madlib_updates(self):
        """Test that multiple madlibs can have different image URLs"""
        # Create second madlib
        madlib_id_2 = self.madlib_service.new_filled_madlib(
            template_id=self.template_id,  # type: ignore[arg-type]
            creator_id=self.creator_id,  # type: ignore[arg-type]
            inputted_blanks=[{"id": "1", "input": "test2"}]
        )
        assert madlib_id_2 is not None, "Failed to create second test madlib"  # type: ignore[assert-type]

        try:
            # Update both with different URLs
            url_1 = "https://s3.example.com/image1.png"
            url_2 = "https://s3.example.com/image2.png"

            self.madlib_service.update_image_url(self.madlib_id, url_1)  # type: ignore[arg-type]
            self.madlib_service.update_image_url(madlib_id_2, url_2)  # type: ignore[arg-type]

            # Verify each has correct URL
            madlib_1 = self.madlib_service.get_by_id(self.madlib_id)  # type: ignore[arg-type]
            madlib_2 = self.madlib_service.get_by_id(madlib_id_2)  # type: ignore[arg-type]
            assert madlib_1 is not None and madlib_2 is not None  # type: ignore[assert-type]

            self.assertEqual(madlib_1['image_url'], url_1)
            self.assertEqual(madlib_2['image_url'], url_2)

        finally:
            # Cleanup
            self.madlib_service.delete_filled_madlib(madlib_id_2)
