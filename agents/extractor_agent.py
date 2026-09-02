import json
from utils.bedrock_utils import invoke_bedrock_llm
from utils.logger import get_logger

logger = get_logger("extractor_agent")

SYSTEM_PROMPT = """You are a Legal Clause Extraction Agent.
Your goal is to parse raw contract text and segment it into structured legal clauses. Evaluate and classify each clause.

FEW-SHOT EXAMPLE:
Input: "The Receiving Party shall keep the Information confidential for a period of 5 years."
Output:
{
 "contract_type": "NDA",
 "clauses": [
   {
     "clause_name": "Confidentiality Term",
     "raw_text": "The Receiving Party shall keep the Information confidential for a period of 5 years.",
     "clause_category": "Confidentiality / Non-Disclosure",
     "classification_rationale": "Explicitly states the duration and obligation of keeping information confidential.",
     "confidence_score": 0.98
   }
 ]
}

Extract clauses and classify them.
Return ONLY valid JSON matching this schema:
{
 "contract_type": "NDA | MSA | SOW | Consulting",
 "clauses": [
   {
     "clause_name": "Name of the clause",
     "raw_text": "Exact raw text...",
     "clause_category": "Category classification",
     "classification_rationale": "Why it was classified this way",
     "confidence_score": <Float between 0.0 and 1.0 representing precision/credibility>
   }
 ]
}"""

class ExtractorAgent:
    def process(self, document_text: str) -> dict:
        logger.info("ExtractorAgent: Segmenting and classifying clauses.")
        prompt = f"Extract all clauses from the following text:\n\n{document_text}\n\nOutput JSON strictly."
        raw_response = invoke_bedrock_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        clean_json = raw_response.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_json)
        except Exception:
            return {"contract_type": "Unknown", "clauses": []}
