import json
import boto3
from botocore.exceptions import ClientError
from config import AWS_REGION, BEDROCK_MODEL_ID
from utils.logger import get_logger

logger = get_logger("bedrock_utils")

def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)

def invoke_bedrock_llm(prompt: str, system_prompt: str = "You are an expert enterprise legal AI assistant.", max_tokens: int = 4096, temperature: float = 0.0) -> str:
    client = get_bedrock_client()
    try:
        logger.info(f"Invoking Bedrock model {BEDROCK_MODEL_ID}")
        response = client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system=[{"text": system_prompt}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature}
        )
        return response["output"]["message"]["content"][0]["text"]
    except ClientError as err:
        logger.error(f"Bedrock invocation failed: {err.response['Error']['Message']}")
        raise err
