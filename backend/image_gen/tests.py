from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from bson import ObjectId
from io import BytesIO
from PIL import Image

from image_gen.models import ImageGenerationModel
from image_gen.utils import upload_ai_image
from image_gen.views import ImageGenerationViewSet
from madlibs.models import UserFilledMadlibs, MadLibTemplate


class ImageGenerationModelTest(TestCase):
    """Test suite for ImageGenerationModel"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_madlib_text = "Once upon a time there was a big dog"
        self.test_madlib_id = str(ObjectId())

    @patch('image_gen.models.tempfile.NamedTemporaryFile')
    @patch('image_gen.models.upload_ai_image')
    @patch('image_gen.models.genai.Client')
    def test_create_image_success(self, mock_client_class, mock_upload, mock_temp_file):
        """Test successful image generation"""
        # Mock the Gemini API response
        mock_image = Mock()
        mock_image.image = Mock()

        mock_response = Mock()
        mock_response.generated_images = [mock_image]

        mock_client = Mock()
        mock_client.models.generate_images.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Mock temp file
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_image.png'
        mock_temp_file.return_value = mock_temp

        # Mock S3 upload
        expected_url = "https://s3.example.com/madlibs/test/image.png"
        mock_upload.return_value = expected_url

        # Create model AFTER mocks are in place
        model = ImageGenerationModel()

        # Generate image
        result = model.create_image(
            madlib_text=self.test_madlib_text,
            madlib_id=self.test_madlib_id
        )

        # Assertions
        self.assertEqual(result, expected_url)
        mock_client.models.generate_images.assert_called_once()
        mock_upload.assert_called_once()

    @patch('image_gen.models.tempfile.NamedTemporaryFile')
    @patch('image_gen.models.upload_ai_image')
    @patch('image_gen.models.genai.Client')
    def test_create_image_with_style_args(self, mock_client_class, mock_upload, mock_temp_file):
        """Test image generation with extra prompt arguments"""
        mock_image = Mock()
        mock_image.image = Mock()

        mock_response = Mock()
        mock_response.generated_images = [mock_image]

        mock_client = Mock()
        mock_client.models.generate_images.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Mock temp file
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_image.png'
        mock_temp_file.return_value = mock_temp

        mock_upload.return_value = "https://s3.example.com/test.png"

        # Create model AFTER mocks are in place
        model = ImageGenerationModel()

        extra_args = {
            'style': 'watercolor painting',
            'aspect_ratio': '16:9'
        }

        result = model.create_image(
            madlib_text=self.test_madlib_text,
            madlib_id=self.test_madlib_id,
            extra_prompt_args=extra_args
        )

        self.assertIsNotNone(result)
        
        # Verify the config was built with the extra args
        call_kwargs = mock_client.models.generate_images.call_args.kwargs
        self.assertEqual(call_kwargs['config']['aspect_ratio'], '16:9')

    @patch('image_gen.models.genai.Client')
    def test_create_image_no_images_generated(self, mock_client_class):
        """Test when API returns no images"""
        mock_response = Mock()
        mock_response.generated_images = []

        mock_client = Mock()
        mock_client.models.generate_images.return_value = mock_response
        mock_client_class.return_value = mock_client

        model = ImageGenerationModel()

        result = model.create_image(
            madlib_text=self.test_madlib_text,
            madlib_id=self.test_madlib_id
        )

        self.assertIsNone(result)

    @patch('image_gen.models.genai.Client')
    def test_create_image_api_exception(self, mock_client_class):
        """Test handling of API exceptions"""
        mock_client = Mock()
        mock_client.models.generate_images.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        model = ImageGenerationModel()

        result = model.create_image(
            madlib_text=self.test_madlib_text,
            madlib_id=self.test_madlib_id
        )

        self.assertIsNone(result)

    @patch('image_gen.models.genai.Client')
    def test_build_generation_config_defaults(self, mock_client_class):
        """Test generation config with default values"""
        mock_client_class.return_value = Mock()
        model = ImageGenerationModel()

        config = model._build_generation_config(None)

        self.assertEqual(config['number_of_images'], 1)
        self.assertEqual(config['aspect_ratio'], '1:1')

    @patch('image_gen.models.genai.Client')
    def test_build_generation_config_custom(self, mock_client_class):
        """Test generation config with custom values"""
        mock_client_class.return_value = Mock()
        model = ImageGenerationModel()

        extra_args = {
            'aspect_ratio': '4:3',
        }
        config = model._build_generation_config(extra_args)

        self.assertEqual(config['aspect_ratio'], '4:3')

    @patch('image_gen.models.genai.Client')
    @patch('image_gen.models.IMAGE_GENERATION_SYS_PROMPT', 'System prompt here')
    def test_build_full_prompt_with_system_prompt(self, mock_client_class):
        """Test prompt building with system prompt"""
        mock_client_class.return_value = Mock()
        model = ImageGenerationModel()

        extra_args = {'style': 'anime'}
        prompt = model._build_full_prompt(
            self.test_madlib_text,
            extra_args
        )

        self.assertIn('System prompt here', prompt)
        self.assertIn(self.test_madlib_text, prompt)
        self.assertIn('anime', prompt)

    @patch('image_gen.models.genai.Client')
    def test_build_full_prompt_without_extras(self, mock_client_class):
        """Test prompt building without extra arguments"""
        mock_client_class.return_value = Mock()
        model = ImageGenerationModel()

        prompt = model._build_full_prompt(self.test_madlib_text, None)
        self.assertIn(self.test_madlib_text, prompt)


class UtilsTest(TestCase):
    """Test suite for utility functions"""

    @patch('image_gen.utils.boto3.client')
    @patch('image_gen.utils.settings')
    def test_upload_ai_image_success(self, mock_settings, mock_boto_client):
        """Test successful image upload to S3"""
        # Mock S3 client
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3

        # Mock settings with proper string values
        mock_settings.AWS_ACCESS_KEY_ID = 'test-access-key'
        mock_settings.AWS_SECRET_ACCESS_KEY = 'test-secret-key'
        mock_settings.AWS_REGION = 'us-east-1'
        mock_settings.AWS_STORAGE_BUCKET_NAME = 'test-bucket'
        mock_settings.AWS_S3_URL = 'https://s3.amazonaws.com/test-bucket'

        test_file = '/tmp/test_image.png'
        test_madlib_id = str(ObjectId())

        result = upload_ai_image(test_file, test_madlib_id)

        # Assertions
        self.assertIsNotNone(result)
        assert result is not None  # type: ignore[assert-type]
        self.assertIn('test-bucket', result)
        self.assertIn(test_madlib_id, result)
        mock_s3.upload_file.assert_called_once()

    @patch('image_gen.utils.boto3.client')
    @patch('image_gen.utils.settings')
    def test_upload_ai_image_failure(self, mock_settings, mock_boto_client):
        """Test S3 upload failure"""
        mock_s3 = Mock()
        mock_s3.upload_file.side_effect = Exception("S3 Error")
        mock_boto_client.return_value = mock_s3

        # Mock settings with proper string values
        mock_settings.AWS_ACCESS_KEY_ID = 'test-access-key'
        mock_settings.AWS_SECRET_ACCESS_KEY = 'test-secret-key'
        mock_settings.AWS_REGION = 'us-east-1'
        mock_settings.AWS_STORAGE_BUCKET_NAME = 'test-bucket'
        mock_settings.AWS_S3_URL = 'https://s3.amazonaws.com/test-bucket'

        result = upload_ai_image('/tmp/test.png', str(ObjectId()))

        self.assertIsNone(result)


class ImageGenerationViewSetTest(APITestCase):
    """Test suite for ImageGenerationViewSet API endpoints"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()

        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create test madlib template and filled madlib
        self.template_service = MadLibTemplate()
        self.template_id = self.template_service.create({
            'title': 'Test Template',
            'story': 'Once upon a time...',
            'blanks': []
        })
        assert self.template_id is not None, "Failed to create test template"  # type: ignore[assert-type]

        self.madlib_service = UserFilledMadlibs()
        # Create a user first
        from users.models import UserOperations
        user_ops = UserOperations()
        self.creator_id = user_ops.create(
            username='testcreator',
            email='creator@test.com',
            oauth_provider='google',
            oauth_id='test_123'
        )
        assert self.creator_id is not None, "Failed to create test user"  # type: ignore[assert-type]

        self.madlib_id = self.madlib_service.new_filled_madlib(
            template_id=self.template_id,
            creator_id=self.creator_id,
            inputted_blanks=[
                {"id": "1", "input": "happy"},
                {"id": "2", "input": "dog"}
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
            from users.models import UserOperations
            UserOperations().delete(self.creator_id)

    @patch('image_gen.views.ImageGenerationModel.create_image')
    def test_generate_image_success(self, mock_create_image):
        """Test successful image generation via API"""
        test_image_url = "https://s3.example.com/test.png"
        mock_create_image.return_value = test_image_url

        data = {
            'madlib_id': self.madlib_id,
            'madlib_text': 'Once upon a time there was a happy dog',
            'extra_prompt_args': {
                'style': 'cartoon',
                'aspect_ratio': '1:1'
            }
        }

        response = self.client.post('/api/image-gen/generate/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['url'], test_image_url)  # type: ignore[attr-defined]
        self.assertEqual(response.data['madlib_id'], self.madlib_id)  # type: ignore[attr-defined]
        mock_create_image.assert_called_once()

        # Verify madlib was updated
        updated_madlib = self.madlib_service.get_by_id(self.madlib_id) # pyright: ignore[reportArgumentType]
        assert updated_madlib is not None  # type: ignore[assert-type]
        self.assertEqual(updated_madlib['image_url'], test_image_url)

    def test_generate_image_missing_fields(self):
        """Test image generation with missing required fields"""
        data = {
            'madlib_id': self.madlib_id
            # Missing madlib_text
        }

        response = self.client.post('/api/image-gen/generate/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)  # type: ignore[attr-defined]

    def test_generate_image_empty_text(self):
        """Test image generation with empty madlib text"""
        data = {
            'madlib_id': self.madlib_id,
            'madlib_text': '   '  # Empty/whitespace only
        }

        response = self.client.post('/api/image-gen/generate/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)  # type: ignore[attr-defined]

    @patch('image_gen.views.ImageGenerationModel.create_image')
    def test_generate_image_generation_fails(self, mock_create_image):
        """Test when image generation fails"""
        mock_create_image.return_value = None

        data = {
            'madlib_id': self.madlib_id,
            'madlib_text': 'Test text'
        }

        response = self.client.post('/api/image-gen/generate/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)  # type: ignore[attr-defined]

    @patch('image_gen.views.ImageGenerationModel.create_image')
    def test_generate_image_invalid_madlib_id(self, mock_create_image):
        """Test image generation with invalid madlib ID"""
        test_image_url = "https://s3.example.com/test.png"
        mock_create_image.return_value = test_image_url

        data = {
            'madlib_id': str(ObjectId()),  # Non-existent madlib
            'madlib_text': 'Test text'
        }

        response = self.client.post('/api/image-gen/generate/', data, format='json')

        # Should succeed in generating but warn about madlib update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('warning', response.data)  # type: ignore[attr-defined]
        self.assertEqual(response.data['url'], test_image_url)  # type: ignore[attr-defined]

    @patch('image_gen.views.upload_ai_image')
    def test_upload_image_success(self, mock_upload):
        """Test successful image upload via API"""
        test_image_url = "https://s3.example.com/uploaded.png"
        mock_upload.return_value = test_image_url

        # Create a test image file
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.name = 'test.png'
        image_file.seek(0)

        data = {
            'madlib_id': self.madlib_id,
            'image': image_file
        }

        response = self.client.post('/api/image-gen/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['url'], test_image_url)  # type: ignore[attr-defined]
        mock_upload.assert_called_once()

        # Verify madlib was updated
        assert self.madlib_id is not None
        updated_madlib = self.madlib_service.get_by_id(self.madlib_id) 
        assert updated_madlib is not None  
        self.assertEqual(updated_madlib['image_url'], test_image_url)

    def test_upload_image_missing_madlib_id(self):
        """Test image upload without madlib_id"""
        image = Image.new('RGB', (100, 100))
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.name = 'test.png'
        image_file.seek(0)

        data = {
            'image': image_file
        }

        response = self.client.post('/api/image-gen/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)  # type: ignore[attr-defined]

    def test_upload_image_missing_file(self):
        """Test image upload without image file"""
        data = {
            'madlib_id': self.madlib_id
        }

        response = self.client.post('/api/image-gen/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)  # type: ignore[attr-defined]

    @patch('image_gen.views.upload_ai_image')
    def test_upload_image_upload_fails(self, mock_upload):
        """Test when S3 upload fails"""
        mock_upload.return_value = None

        image = Image.new('RGB', (100, 100))
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.name = 'test.png'
        image_file.seek(0)

        data = {
            'madlib_id': self.madlib_id,
            'image': image_file
        }

        response = self.client.post('/api/image-gen/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)  # type: ignore[attr-defined]

    def test_generate_image_unauthenticated(self):
        """Test that unauthenticated users cannot generate images"""
        self.client.force_authenticate(user=None) # type: ignore

        data = {
            'madlib_id': self.madlib_id,
            'madlib_text': 'Test text'
        }

        response = self.client.post('/api/image-gen/generate/', data, format='json')

        # DRF returns 403 Forbidden when authentication is required but not provided
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_upload_image_unauthenticated(self):
        """Test that unauthenticated users cannot upload images"""
        self.client.force_authenticate(user=None) # type: ignore

        image = Image.new('RGB', (100, 100))
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.name = 'test.png'
        image_file.seek(0)

        data = {
            'madlib_id': self.madlib_id,
            'image': image_file
        }

        response = self.client.post('/api/image-gen/upload/', data, format='multipart')

        # DRF returns 403 Forbidden when authentication is required but not provided
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class MadlibModelUpdateImageUrlTest(TestCase):
    """Test suite for UserFilledMadlibs.update_image_url method"""

    def setUp(self):
        """Set up test fixtures"""
        self.madlib_service = UserFilledMadlibs()
        self.template_service = MadLibTemplate()

        # Create test template
        self.template_id = self.template_service.create({
            'title': 'Test Template',
            'story': 'Test story',
            'blanks': []
        })
        assert self.template_id is not None, "Failed to create test template"  # type: ignore[assert-type]

        # Create test user
        from users.models import UserOperations
        user_ops = UserOperations()
        self.creator_id = user_ops.create(
            username='testuser_madlib',
            email='test_madlib@test.com',
            oauth_provider='google',
            oauth_id='test_madlib_123'
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
            from users.models import UserOperations
            UserOperations().delete(self.creator_id)

    def test_update_image_url_success(self):
        """Test successfully updating image URL"""
        test_url = "https://s3.example.com/test_image.png"
        assert self.madlib_id is not None

        success = self.madlib_service.update_image_url(self.madlib_id, test_url)

        self.assertTrue(success)

        # Verify the update
        madlib = self.madlib_service.get_by_id(self.madlib_id)
        self.assertIsNotNone(madlib)
        assert madlib is not None 
        self.assertEqual(madlib['image_url'], test_url)
        self.assertIn('updated_at', madlib)

    def test_update_image_url_nonexistent_madlib(self):
        """Test updating image URL for non-existent madlib"""
        fake_id = str(ObjectId())
        test_url = "https://s3.example.com/test.png"

        success = self.madlib_service.update_image_url(fake_id, test_url)

        self.assertFalse(success)

    def test_update_image_url_same_url(self):
        """Test updating with the same URL (should still succeed)"""
        test_url = "https://s3.example.com/same.png"
        assert self.madlib_id is not None

        # First update
        success1 = self.madlib_service.update_image_url(self.madlib_id, test_url)
        self.assertTrue(success1)

        # Second update with same URL
        success2 = self.madlib_service.update_image_url(self.madlib_id, test_url)
        self.assertTrue(success2)

    def test_update_image_url_invalid_id_format(self):
        """Test updating with invalid ObjectId format"""
        test_url = "https://s3.example.com/test.png"

        success = self.madlib_service.update_image_url("invalid_id", test_url)

        self.assertFalse(success)
