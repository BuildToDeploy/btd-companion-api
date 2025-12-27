from app.ai_providers import OpenAIProvider, ClaudeProvider, GrokProvider
from app.models import AIProvider
from app.config import get_settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AIManager:
    """Manages AI provider initialization and fallback logic"""

    def __init__(self):
        self.settings = get_settings()
        self.providers: Dict[AIProvider, Any] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available AI providers"""
        if self.settings.openai_api_key:
            try:
                self.providers[AIProvider.OPENAI] = OpenAIProvider(self.settings.openai_api_key)
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}")

        if self.settings.anthropic_api_key:
            try:
                self.providers[AIProvider.CLAUDE] = ClaudeProvider(self.settings.anthropic_api_key)
                logger.info("Claude provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude provider: {e}")

        if self.settings.xai_api_key:
            try:
                self.providers[AIProvider.GROK] = GrokProvider(self.settings.xai_api_key)
                logger.info("Grok provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Grok provider: {e}")

    def get_provider(self, preferred: AIProvider = AIProvider.OPENAI):
        """Get AI provider with fallback logic"""
        # Try preferred provider first
        if preferred in self.providers:
            logger.info(f"Using preferred provider: {preferred}")
            return self.providers[preferred]

        # Fallback to first available provider
        if self.providers:
            fallback = next(iter(self.providers.values()))
            fallback_name = next(iter(self.providers.keys()))
            logger.warning(f"Preferred provider {preferred} not available, falling back to {fallback_name}")
            return fallback

        raise ValueError("No AI providers available. Please configure at least one API key.")

    async def analyze_contract(self, contract_code: str, provider: AIProvider = AIProvider.OPENAI) -> Dict[str, Any]:
        """Analyze contract with fallback"""
        try:
            ai_provider = self.get_provider(provider)
            return await ai_provider.analyze_contract(contract_code)
        except Exception as e:
            logger.error(f"Analysis failed with {provider}, attempting fallback")
            # Try other providers
            for alt_provider_name, alt_provider in self.providers.items():
                if alt_provider_name != provider:
                    try:
                        logger.info(f"Retrying with {alt_provider_name}")
                        return await alt_provider.analyze_contract(contract_code)
                    except Exception as alt_e:
                        logger.warning(f"{alt_provider_name} also failed: {alt_e}")
            raise

    async def optimize_contract(self, contract_code: str, provider: AIProvider = AIProvider.OPENAI) -> Dict[str, Any]:
        """Optimize contract with fallback"""
        try:
            ai_provider = self.get_provider(provider)
            return await ai_provider.optimize_contract(contract_code)
        except Exception as e:
            logger.error(f"Optimization failed with {provider}, attempting fallback")
            for alt_provider_name, alt_provider in self.providers.items():
                if alt_provider_name != provider:
                    try:
                        logger.info(f"Retrying with {alt_provider_name}")
                        return await alt_provider.optimize_contract(contract_code)
                    except Exception as alt_e:
                        logger.warning(f"{alt_provider_name} also failed: {alt_e}")
            raise

    async def validate_deployment(self, contract_code: str, network: str, provider: AIProvider = AIProvider.OPENAI) -> Dict[str, Any]:
        """Validate deployment with fallback"""
        try:
            ai_provider = self.get_provider(provider)
            return await ai_provider.validate_deployment(contract_code, network)
        except Exception as e:
            logger.error(f"Validation failed with {provider}, attempting fallback")
            for alt_provider_name, alt_provider in self.providers.items():
                if alt_provider_name != provider:
                    try:
                        logger.info(f"Retrying with {alt_provider_name}")
                        return await alt_provider.validate_deployment(contract_code, network)
                    except Exception as alt_e:
                        logger.warning(f"{alt_provider_name} also failed: {alt_e}")
            raise


ai_manager = AIManager()
