import logging
import watchtower
import boto3
from config import AWS_REGION, CLOUDWATCH_LOG_GROUP

def get_logger(name: str = "legal_review") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        try:
            cw_client = boto3.client("logs", region_name=AWS_REGION)
            cw_handler = watchtower.CloudWatchLogHandler(
                log_group_name=CLOUDWATCH_LOG_GROUP, boto3_client=cw_client, create_log_group=True
            )
            cw_handler.setFormatter(formatter)
            logger.addHandler(cw_handler)
        except Exception as e:
            logger.warning(f"CloudWatch logger initialization skipped: {str(e)}")
    return logger
