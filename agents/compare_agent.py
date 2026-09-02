import json
from utils.bedrock_utils import invoke_bedrock_llm
from utils.logger import get_logger

logger = get_logger("compare_agent")

SYSTEM_PROMPT = """You are a Contract Deviation & Comparison Agent.
Perform a context-aware, sentence-level comparison between the Third-Party Clause and the Standard Baseline.

FEW-SHOT EXAMPLE:
Input: Baseline: "Net 30 days." | Third-Party: "Net 60 days."
Output: [
 {
   "clause_name": "Payment Terms",
   "change_type": "MODIFIED",
   "standard_clause_text": "Net 30 days.",
   "contract_clause_text": "Net 60 days.",
   "deviation_details": "Payment duration extended from 30 to 60 days.",
   "confidence_score": 0.99
 }
]

Output ONLY a JSON list of deviations:
[
 {
   "clause_name": "...",
   "change_type": "MODIFIED | ADDED | REMOVED | UNCHANGED",
   "standard_clause_text": "...",
   "contract_clause_text": "...",
   "deviation_details": "Sentence-level details...",
   "confidence_score": <Float 0.0 to 1.0 representing model certainty>
 }
]"""

class CompareAgent:
    def process(self, extracted_clauses: list, standard_template_text: str) -> list:
        logger.info("CompareAgent: Comparing clauses against baseline template.")
        prompt = f"""
Standard Baseline Template:
{standard_template_text}

Third-Party Extracted Clauses:
{json.dumps(extracted_clauses, indent=2)}

Perform a sentence-level comparison and return deviations in JSON format.
"""
        raw_response = invoke_bedrock_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        clean_json = raw_response.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_json)
        except Exception:
            return []
