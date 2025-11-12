from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from social.utils import upload_ai_image
from madlibs.models import UserFilledMadlibs


# Create your views here.












#api for uploading madlib image to s3
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_madlib_image(request, madlib_id):
    """
    Uploads an AI-generated image for a specific Madlib.
    """
    file = request.FILES.get('image')
    if not file:
        return Response({'error': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    url = upload_ai_image(file, madlib_id)

    if url:
        madlib_service = UserFilledMadlibs()
        madlib_service.update_filled_madlib(madlib_id, {"image_url": url})
        return Response({'url': url, 'message': 'Image uploaded successfully!'})
    else:
        return Response({'error': 'Upload failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
