from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models import AIProvider


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    name: str


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ContractBase(BaseModel):
    name: str
    source_code: str
    network: str


class ContractCreate(ContractBase):
    pass


class ContractResponse(ContractBase):
    id: int
    address: Optional[str]
    language: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    contract_id: Optional[int] = None
    source_code: Optional[str] = None
    provider: AIProvider = AIProvider.OPENAI


class SecurityFinding(BaseModel):
    severity: str  # critical, high, medium, low
    title: str
    description: str


class AnalysisResponse(BaseModel):
    security_findings: List[SecurityFinding]
    risk_score: int
    explanation: str
    execution_time_ms: float
    provider_used: AIProvider


class OptimizationRequest(BaseModel):
    contract_id: Optional[int] = None
    source_code: Optional[str] = None
    provider: AIProvider = AIProvider.OPENAI


class OptimizationSuggestion(BaseModel):
    area: str
    suggestion: str
    potential_savings: Optional[str]


class OptimizationResponse(BaseModel):
    suggestions: List[OptimizationSuggestion]
    execution_time_ms: float
    provider_used: AIProvider


class DeploymentRequest(BaseModel):
    contract_id: int
    network: str
    constructor_args: Optional[Dict[str, Any]] = None


class DeploymentResponse(BaseModel):
    is_valid: bool
    network: str
    estimated_gas: Optional[int]
    warnings: List[str]
    execution_time_ms: float


class MonitoringResponse(BaseModel):
    contract_id: int
    status: str
    last_checked: datetime
    events_count: int

    class Config:
        from_attributes = True
