import os
import boto3
from botocore.exceptions import ClientError
from config import AWS_REGION, S3_BUCKET_NAME
from utils.logger import get_logger

logger = get_logger("s3_utils")

def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)

def upload_file_to_s3(file_path: str, object_name: str = None) -> bool:
    s3 = get_s3_client()
    if object_name is None: object_name = os.path.basename(file_path)
    try:
        s3.upload_file(file_path, S3_BUCKET_NAME, object_name)
        return True
    except ClientError as e:
        logger.error(f"S3 upload error: {e}")
        return False

def get_template_from_s3(template_key: str) -> str:
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=template_key)
        return response["Body"].read().decode("utf-8")
    except ClientError as e:
        logger.warning(f"Failed to fetch template from S3. Error: {e}")
        return ""
