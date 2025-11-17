import boto3
import os
from uuid import uuid4
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def upload_ai_image(file, madlib_id):
    """
    Upload an AI-generated image to S3 and return its public URL.
    """
    # Create S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    file_key = f"madlibs/{madlib_id}/{uuid4()}.png"

    try:
        s3.upload_file(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_key,
            ExtraArgs={'ContentType': 'image/png'}
        )

        return f"{settings.AWS_S3_URL}/{file_key}"
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        return None
