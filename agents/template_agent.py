import os
from utils.s3_utils import get_template_from_s3
from utils.logger import get_logger

logger = get_logger("template_agent")

class TemplateAgent:
   def __init__(self, templates_dir: str = "templates"):
       self.templates_dir = templates_dir

   def get_template(self, contract_type: str) -> str:
       key = f"{contract_type.lower()}.txt"
       logger.info(f"TemplateAgent: Fetching standard baseline for {contract_type}")
       
       # Try S3 first
       content = get_template_from_s3(f"templates/{key}")
       if content:
           return content
       
       # Fallback to local directory
       local_path = os.path.join(self.templates_dir, key)
       if os.path.exists(local_path):
           with open(local_path, "r", encoding="utf-8") as f:
               return f.read()
       
       return "Standard terms apply. No specific benchmark template found."
