from app.ai_providers.base import BaseAIProvider
from typing import Dict, Any
import json
import logging
import httpx

logger = logging.getLogger(__name__)


class GrokProvider(BaseAIProvider):
    """Grok (xAI) provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def analyze_contract(self, contract_code: str) -> Dict[str, Any]:
        """Analyze contract using Grok"""
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
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "grok-1",
                        "messages": [
                            {"role": "system", "content": "You are a smart contract security auditor. Analyze contracts and provide detailed security findings."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                    }
                )
                response.raise_for_status()
                data = response.json()
                
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            return {
                "findings": parsed.get("security_findings", []),
                "risk_score": parsed.get("risk_score", 0),
                "explanation": parsed.get("explanation", ""),
                "execution_time_ms": self._get_execution_time_ms(),
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Grok response as JSON")
            raise
        except Exception as e:
            logger.error(f"Grok API error: {str(e)}")
            raise

    async def optimize_contract(self, contract_code: str) -> Dict[str, Any]:
        """Suggest optimizations using Grok"""
        self._start_timer()
        
        prompt = f"""Analyze the following Solidity contract for gas optimization opportunities.

Contract Code:
{contract_code}

Provide a JSON response with:
1. suggestions: List of optimization suggestions with area, suggestion, potential_savings
2. summary: Brief summary

Return ONLY valid JSON."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "grok-1",
                        "messages": [
                            {"role": "system", "content": "You are a Solidity gas optimization expert. Provide actionable optimization suggestions."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                    }
                )
                response.raise_for_status()
                data = response.json()
                
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            return {
                "suggestions": parsed.get("suggestions", []),
                "summary": parsed.get("summary", ""),
                "execution_time_ms": self._get_execution_time_ms(),
            }
        except Exception as e:
            logger.error(f"Grok optimization error: {str(e)}")
            raise

    async def validate_deployment(self, contract_code: str, network: str) -> Dict[str, Any]:
        """Validate deployment using Grok"""
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
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "grok-1",
                        "messages": [
                            {"role": "system", "content": f"You are a blockchain deployment validator for {network} network."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                    }
                )
                response.raise_for_status()
                data = response.json()
                
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            return {
                "is_valid": parsed.get("is_valid", True),
                "warnings": parsed.get("warnings", []),
                "estimated_gas": parsed.get("estimated_gas"),
                "notes": parsed.get("notes", ""),
                "execution_time_ms": self._get_execution_time_ms(),
            }
        except Exception as e:
            logger.error(f"Grok validation error: {str(e)}")
            raise
