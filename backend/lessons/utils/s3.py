import boto3
import os
import logging
from botocore.exceptions import ClientError
from django.conf import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_file(local_file_path: str, s3_folder="audio") -> str:
    """
    Upload local file to Arvan S3 using boto3.resource.
    Returns the uploaded file URL.
    """
    try:
        s3_resource = boto3.resource(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            verify=False,
        )
    except Exception as exc:
        logger.error(f"Failed to create S3 resource: {exc}")
        raise

    key_name = f"{s3_folder}/{os.path.basename(local_file_path)}"
    
    try:

        bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        with open(local_file_path, "rb") as file:
            bucket.put_object(
                ACL='public-read',  # or 'private' if needed
                Body=file,
                Key=key_name
            )
        logger.info(f"File uploaded successfully: {key_name}")
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise

    return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{key_name}"
