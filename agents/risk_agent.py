import json
from utils.bedrock_utils import invoke_bedrock_llm
from utils.logger import get_logger

logger = get_logger("risk_agent")

SYSTEM_PROMPT = """You are a Legal Risk & Compliance Classifier Agent.
Analyze each clause deviation, classify it by Risk and Business Impact, and assign an evaluation credibility score.

FEW-SHOT EXAMPLE:
Input Deviation: "Payment duration extended from 30 to 60 days."
Output:
[
 {
   "clause_name": "Payment Terms",
   "risk_level": "MEDIUM",
   "business_impact": "Delays accounts receivable by 30 days, impacting cash flow.",
   "mitigation_recommendation": "Reject 60 days; propose Net 45 days max.",
   "confidence_score": 0.95
 }
]

Risk Levels:
- HIGH: Unlimited liability, missing IP, unfavorable law.
- MEDIUM: Strict termination, aggressive payment.
- LOW: Minor grammar changes.

Return ONLY a JSON list:
[
 {
   "clause_name": "...",
   "risk_level": "HIGH | MEDIUM | LOW",
   "business_impact": "...",
   "mitigation_recommendation": "...",
   "confidence_score": <Float 0.0 to 1.0>
 }
]"""

class RiskAgent:
    def process(self, deviations: list) -> list:
        logger.info("RiskAgent: Analyzing legal risks and impact.")
        prompt = f"Classify the following deviations by risk and impact:\n{json.dumps(deviations, indent=2)}\n\nOutput JSON strictly."
        raw_response = invoke_bedrock_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        clean_json = raw_response.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_json)
        except Exception:
            return []
