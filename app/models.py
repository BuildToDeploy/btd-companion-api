from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class AIProvider(str, enum.Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GROK = "grok"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    api_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    api_requests = relationship("AIRequest", back_populates="user")
    contracts = relationship("Contract", back_populates="user")
    simulation_results = relationship("SimulationResult", back_populates="user")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key = Column(String, unique=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)


class AIRequest(Base):
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    provider_used = Column(Enum(AIProvider))
    request_type = Column(String)  # analyze, optimize, deploy
    execution_time_ms = Column(Float)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="api_requests")
    contract = relationship("Contract", back_populates="ai_requests")
    result = relationship("AnalysisResult", uselist=False, back_populates="request")
    simulation_results = relationship("SimulationResult", back_populates="request")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    address = Column(String, index=True, nullable=True)
    source_code = Column(Text)
    network = Column(String)  # ethereum, polygon, arbitrum, etc
    language = Column(String, default="solidity")  # solidity, vyper, etc
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="contracts")
    ai_requests = relationship("AIRequest", back_populates="contract")
    analysis_results = relationship("AnalysisResult", back_populates="contract")
    monitoring = relationship("Monitoring", back_populates="contract")
    simulation_results = relationship("SimulationResult", back_populates="contract")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("ai_requests.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    analysis_type = Column(String)  # security, optimization, deployment
    risk_score = Column(Integer, nullable=True)  # 0-100
    findings = Column(JSON)  # List of findings
    suggestions = Column(JSON)  # List of suggestions
    raw_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("AIRequest", back_populates="result")
    contract = relationship("Contract", back_populates="analysis_results")


class Monitoring(Base):
    __tablename__ = "monitoring"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    last_checked = Column(DateTime)
    status = Column(String)  # active, inactive, error
    events_count = Column(Integer, default=0)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="monitoring")


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    request_id = Column(Integer, ForeignKey("ai_requests.id"))
    simulation_type = Column(String)  # transaction, scenario, failure_path
    calldata = Column(Text)
    state_assumptions = Column(JSON)
    result_status = Column(String)  # success, reverted, error, warning
    gas_used = Column(Integer, nullable=True)
    execution_trace = Column(JSON, nullable=True)
    findings = Column(JSON)
    ai_insights = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", foreign_keys=[contract_id])
    user = relationship("User", foreign_keys=[user_id])
    request = relationship("AIRequest", foreign_keys=[request_id])
    scenarios = relationship("SimulationScenario", back_populates="simulation")


class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_results.id"))
    scenario_name = Column(String)  # e.g., "owner_change_scenario"
    description = Column(Text)
    initial_state = Column(JSON)
    modified_state = Column(JSON)
    expected_behavior = Column(Text)
    actual_behavior = Column(Text, nullable=True)
    outcome = Column(String)  # success, reverted, unexpected
    ai_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship("SimulationResult", back_populates="scenarios")


class FailurePath(Base):
    __tablename__ = "failure_paths"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_results.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    path_description = Column(Text)
    severity = Column(String)  # critical, high, medium, low
    trigger_conditions = Column(JSON)
    consequences = Column(JSON)
    mitigation_steps = Column(JSON)
    ai_reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", foreign_keys=[contract_id])
