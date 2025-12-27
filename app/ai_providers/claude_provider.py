from app.ai_providers.base import BaseAIProvider
from typing import Dict, Any
import json
import logging
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseAIProvider):
    """Claude (Anthropic) provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)

    async def analyze_contract(self, contract_code: str) -> Dict[str, Any]:
        """Analyze contract using Claude"""
        self._start_timer()
        
        prompt = f"""Analyze the following Solidity smart contract for security vulnerabilities and risks.
        
Contract Code:
{contract_code}

Provide a JSON response with:
1. security_findings: List of findings with severity, title, description
2. risk_score: Overall risk score 0-100
3. explanation: Brief explanation of the analysis

Return ONLY valid JSON."""

        try:
            message = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                system="You are a smart contract security auditor. Analyze contracts and provide detailed security findings.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            parsed = json.loads(content)
            
            return {
                "findings": parsed.get("security_findings", []),
                "risk_score": parsed.get("risk_score", 0),
                "explanation": parsed.get("explanation", ""),
                "execution_time_ms": self._get_execution_time_ms(),
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude response as JSON")
            raise
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise

    async def optimize_contract(self, contract_code: str) -> Dict[str, Any]:
        """Suggest optimizations using Claude"""
        self._start_timer()
        
        prompt = f"""Analyze the following Solidity contract for gas optimization opportunities.

Contract Code:
{contract_code}

Provide a JSON response with:
1. suggestions: List of optimization suggestions with area, suggestion, potential_savings
2. summary: Brief summary

Return ONLY valid JSON."""

        try:
            message = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                system="You are a Solidity gas optimization expert. Provide actionable optimization suggestions.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            parsed = json.loads(content)
            
            return {
                "suggestions": parsed.get("suggestions", []),
                "summary": parsed.get("summary", ""),
                "execution_time_ms": self._get_execution_time_ms(),
            }
        except Exception as e:
            logger.error(f"Claude optimization error: {str(e)}")
            raise

    async def validate_deployment(self, contract_code: str, network: str) -> Dict[str, Any]:
        """Validate deployment using Claude"""
        self._start_timer()
        
        prompt = f"""Validate this Solidity contract for deployment on {network} network.

Contract Code:
{contract_code}

Provide a JSON response with:
1. is_valid: boolean
2. warnings: list of warnings
3. estimated_gas: rough gas estimate for deployment
4. notes: deployment notes

Return ONLY valid JSON."""

        try:
            message = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=f"You are a blockchain deployment validator for {network} network.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            parsed = json.loads(content)
            
            return {
                "is_valid": parsed.get("is_valid", True),
                "warnings": parsed.get("warnings", []),
                "estimated_gas": parsed.get("estimated_gas"),
                "notes": parsed.get("notes", ""),
                "execution_time_ms": self._get_execution_time_ms(),
            }
        except Exception as e:
            logger.error(f"Claude validation error: {str(e)}")
            raise
