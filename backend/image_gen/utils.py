import boto3
import os
from uuid import uuid4
from django.conf import settings

def upload_ai_image(file, madlib_id):
    """
    Upload an AI-generated image to S3 and return its public URL.
    """
    s3 = settings.s3_client
    file_key = f"madlibs/{madlib_id}/{uuid4()}.png"

    try:
        s3.upload_file(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_key,
            ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'}
        )

        return f"{settings.AWS_S3_URL}/{file_key}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
