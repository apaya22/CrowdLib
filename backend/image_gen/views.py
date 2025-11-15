from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from madlibs.models import UserFilledMadlibs
from .models import ImageGenerationModel
from .utils import upload_ai_image
import logging

logger = logging.getLogger(__name__)


class ImageGenerationViewSet(viewsets.ViewSet):
    """
    API endpoints for generating and managing AI-generated images.

    - POST /api/image-gen/generate/ : Generate an image for a madlib
    - POST /api/image-gen/upload/ : Upload a pre-generated image
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_gen_model = ImageGenerationModel()
        self.madlib_service = UserFilledMadlibs()

    def get_permissions(self):
        """
        permission dictionary. Automatically called by rest_framework.permissions
        """
        permission_classes = {
            'generate': [permissions.IsAuthenticated],
            'upload': [permissions.IsAuthenticated],
        }

        return [
            permission()
            for permission in permission_classes.get(self.action, [permissions.IsAdminUser])
        ]

    def _handle_image_url_update(self, image_url, madlib_id, operation_name):
        """
        Helper method to update madlib db collection with image URL and handle response.

        Args:
            image_url: URL of the uploaded image
            madlib_id: ID of the madlib to update
            operation_name: Name of the operation (e.g., 'generated', 'uploaded') for logging

        Returns:
            Response object
        """
        success = self.madlib_service.update_image_url(madlib_id, image_url)

        if not success:
            logger.warning(f"Image {operation_name} but failed to update image url madlib collection")
            return Response(
                {
                    'url': image_url,
                    'warning': f'Image {operation_name} but madlib update failed'
                },
                status=status.HTTP_200_OK
            )

        logger.info(f"Successfully {operation_name} and updated image for madlib: {madlib_id}")
        return Response(
            {
                'url': image_url,
                'madlib_id': madlib_id,
                'message': f'Image {operation_name} and uploaded successfully'
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate an AI image for a madlib and update the madlib with the image URL.

        Expected JSON:
        {
            "madlib_id": "507f1f77bcf86cd799439011",
            "madlib_text": "Once upon a time there was a big dog",
            "extra_prompt_args": {
                "style": "watercolor painting",
                "aspect_ratio": "16:9",
                "image_size": "2K",
                "person_generation": "allow_all"
            }
        }

        POST /api/image-gen/generate/
        """
        try:
            data = request.data
            logger.debug(f"Generating image for madlib: {data.get('madlib_id', 'N/A')}")

            # Validate required fields
            required_fields = ['madlib_id', 'madlib_text']
            if not all(field in data for field in required_fields):
                logger.warning("Missing required fields in image generation request")
                return Response(
                    {'error': f'Missing required fields: {required_fields}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            madlib_id = data['madlib_id']
            madlib_text = data['madlib_text']
            extra_prompt_args = data.get('extra_prompt_args', None)

            # Validate madlib_text is not empty
            if not madlib_text.strip():
                logger.warning("Empty madlib_text in image generation request")
                return Response(
                    {'error': 'madlib_text cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate and upload image to AWS
            image_url = self.image_gen_model.create_image(
                madlib_text=madlib_text,
                madlib_id=madlib_id,
                extra_prompt_args=extra_prompt_args
            )

            if not image_url:
                logger.error(f"Failed to generate image for madlib: {madlib_id}")
                return Response(
                    {'error': 'Failed to generate or upload image'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Update madlib collection with the image URL
            return self._handle_image_url_update(image_url, madlib_id, 'generated')

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload a pre-generated image file to S3 and update madlib.

        Expected form-data:
        - image: image file
        - madlib_id: ID of the madlib

        POST /api/image-gen/upload/
        """
        try:
            madlib_id = request.data.get('madlib_id')
            file = request.FILES.get('image')

            logger.debug(f"Uploading image for madlib: {madlib_id}")

            # Validate required fields
            if not madlib_id:
                logger.warning("Missing madlib_id in image upload request")
                return Response(
                    {'error': 'madlib_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not file:
                logger.warning("No image file provided in upload request")
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Upload image to S3
            url = upload_ai_image(file, madlib_id)

            if not url:
                logger.error(f"Failed to upload image for madlib: {madlib_id}")
                return Response(
                    {'error': 'Upload failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Update madlib with the image URL
            return self._handle_image_url_update(url, madlib_id, 'uploaded')

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
