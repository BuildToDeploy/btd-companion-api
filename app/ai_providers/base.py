from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.start_time = None

    @abstractmethod
    async def analyze_contract(self, contract_code: str) -> Dict[str, Any]:
        """Analyze smart contract for security issues"""
        pass

    @abstractmethod
    async def optimize_contract(self, contract_code: str) -> Dict[str, Any]:
        """Suggest gas optimizations"""
        pass

    @abstractmethod
    async def validate_deployment(self, contract_code: str, network: str) -> Dict[str, Any]:
        """Validate deployment configuration"""
        pass

    def _start_timer(self):
        """Start execution timer"""
        self.start_time = time.time()

    def _get_execution_time_ms(self) -> float:
        """Get execution time in milliseconds"""
        if self.start_time is None:
            return 0
        return (time.time() - self.start_time) * 1000

    async def _call_api(self, method: str, *args, **kwargs):
        """Wrapper for API calls with error handling"""
        self._start_timer()
        try:
            result = await method(*args, **kwargs)
            logger.info(f"API call successful, execution time: {self._get_execution_time_ms()}ms")
            return result
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise
