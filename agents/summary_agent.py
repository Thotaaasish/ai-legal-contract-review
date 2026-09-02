from utils.bedrock_utils import invoke_bedrock_llm
from utils.logger import get_logger
import json

logger = get_logger("summary_agent")

SYSTEM_PROMPT = """You are an Executive Legal Review Summary Agent.
Provide a clear, professional executive summary of the contract review findings, incorporating Human-in-the-Loop reviewed data."""

class SummaryAgent:
    def process(self, contract_type: str, deviations: list, human_reviewed_risks: list) -> str:
        logger.info("SummaryAgent: Generating final executive legal summary from HITL data.")
        prompt = f"""
Contract Type: {contract_type}
Deviations Identified:
{json.dumps(deviations, indent=2)}

Final Human-Reviewed Risk Matrix:
{json.dumps(human_reviewed_risks, indent=2)}

Generate an executive legal summary containing:
1. Executive Assessment (Go / No-Go / Review Needed)
2. Critical High-Risk Deviations (Referencing the Human-Reviewed Risk Matrix)
3. Actionable Negotiation Points for Counsel
"""
        return invoke_bedrock_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT)
