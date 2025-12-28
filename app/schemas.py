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


# Simulation-related schemas
class SimulationStateAssumption(BaseModel):
    address: str
    balance: Optional[str] = None
    storage_values: Optional[Dict[str, Any]] = None
    nonce: Optional[int] = None


class TransactionSimulationRequest(BaseModel):
    contract_id: Optional[int] = None
    source_code: Optional[str] = None
    calldata: str
    state_assumptions: Optional[List[SimulationStateAssumption]] = None
    from_address: Optional[str] = None
    value: Optional[str] = "0"
    provider: AIProvider = AIProvider.OPENAI


class SimulationFinding(BaseModel):
    type: str  # execution_failure, unexpected_behavior, optimization_opportunity
    severity: str
    description: str
    line_number: Optional[int] = None


class TransactionSimulationResponse(BaseModel):
    simulation_id: int
    status: str  # success, reverted, error
    gas_used: Optional[int]
    execution_trace: Optional[Dict[str, Any]]
    findings: List[SimulationFinding]
    ai_insights: str
    execution_time_ms: float
    provider_used: AIProvider


class WhatIfScenarioRequest(BaseModel):
    contract_id: Optional[int] = None
    source_code: Optional[str] = None
    scenario_description: str  # e.g., "What if owner changes the fee to 50%?"
    function_to_test: str
    initial_state: Dict[str, Any]
    modified_state: Dict[str, Any]
    provider: AIProvider = AIProvider.OPENAI


class ScenarioAnalysis(BaseModel):
    scenario_name: str
    description: str
    expected_behavior: str
    actual_behavior: Optional[str]
    outcome: str  # success, reverted, unexpected
    ai_analysis: str


class WhatIfScenarioResponse(BaseModel):
    scenarios: List[ScenarioAnalysis]
    summary: str
    recommendations: List[str]
    execution_time_ms: float
    provider_used: AIProvider


class FailurePathRequest(BaseModel):
    contract_id: Optional[int] = None
    source_code: Optional[str] = None
    provider: AIProvider = AIProvider.OPENAI


class FailurePathDetail(BaseModel):
    path_description: str
    severity: str
    trigger_conditions: List[str]
    consequences: List[str]
    mitigation_steps: List[str]
    ai_reasoning: str


class FailurePathResponse(BaseModel):
    contract_id: int
    failure_paths: List[FailurePathDetail]
    overall_risk_assessment: str
    execution_time_ms: float
    provider_used: AIProvider


# Contract Intent Verification schemas
class IntentVerificationRequest(BaseModel):
    contract_id: Optional[int] = None
    source_code: Optional[str] = None
    contract_name: Optional[str] = None
    readme_or_comments: Optional[str] = None
    provider: AIProvider = AIProvider.OPENAI


class HiddenLogicDetailResponse(BaseModel):
    logic_type: str
    description: str
    location: str
    line_numbers: List[int]
    risk_level: str
    explanation: str

    class Config:
        from_attributes = True


class MaliciousPatternResponse(BaseModel):
    pattern_type: str
    pattern_name: str
    description: str
    indicators: List[str]
    affected_functions: List[str]
    severity: str
    ai_reasoning: str

    class Config:
        from_attributes = True


class IntentVsBehaviorAnalysis(BaseModel):
    documented_intent: str
    actual_behavior: str
    intent_match_score: int  # 0-100
    mismatches: List[str]


class HiddenLogicAnalysis(BaseModel):
    hidden_logic_detected: bool
    dead_code_areas: List[HiddenLogicDetailResponse]
    delayed_execution_logic: List[HiddenLogicDetailResponse]
    conditional_activation: List[HiddenLogicDetailResponse]


class MaliciousPatternAnalysis(BaseModel):
    malicious_patterns_found: bool
    rug_pull_indicators: List[MaliciousPatternResponse]
    honeypot_indicators: List[MaliciousPatternResponse]
    malicious_risk_score: int  # 0-100


class IntentVerificationResponse(BaseModel):
    verification_id: int
    contract_id: int
    intent_analysis: IntentVsBehaviorAnalysis
    hidden_logic_analysis: HiddenLogicAnalysis
    malicious_pattern_analysis: MaliciousPatternAnalysis
    overall_trust_score: int  # 0-100
    ai_recommendation: str
    execution_time_ms: float
    provider_used: AIProvider

    class Config:
        from_attributes = True
