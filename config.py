import os
import boto3
import json
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"
S3_BUCKET_NAME = os.getenv("LEGAL_S3_BUCKET", "legal-contract-review-capstone")
CLOUDWATCH_LOG_GROUP = "/aws/ec2/legal-contract-review"
SECRET_NAME = "legal_review/api_config"

def get_secret(secret_name: str = SECRET_NAME, region_name: str = AWS_REGION) -> dict:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in get_secret_value_response:
            return json.loads(get_secret_value_response["SecretString"])
    except ClientError as e:
        return {}
    return {}
