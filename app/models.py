from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class AIProvider(str, enum.Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GROK = "grok"


class Blockchain(str, enum.Enum):
    """Supported blockchains"""
    # EVM chains
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    BASE = "base"
    XLAYER = "xlayer"
    
    # Non-EVM chains
    SOLANA = "solana"
    COSMOS = "cosmos"
    ALGORAND = "algorand"
    APTOS = "aptos"
    SUI = "sui"
    PEAQ = "peaq"
    SEI = "sei"


class SmartContractLanguage(str, enum.Enum):
    """Supported smart contract languages"""
    # EVM
    SOLIDITY = "solidity"
    VYPER = "vyper"
    
    # Solana
    RUST = "rust"
    
    # Cosmos
    COSMWASM = "cosmwasm"
    
    # Algorand
    TEAL = "teal"
    PYTEAL = "pyteal"
    
    # Aptos/Sui
    MOVE = "move"


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
    intent_verifications = relationship("IntentVerification", back_populates="user")
    x402_payments = relationship("X402Payment", back_populates="user")
    x402_subscriptions = relationship("X402Subscription", back_populates="user")


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
    intent_verification = relationship("IntentVerification", back_populates="request")


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
    intent_verifications = relationship("IntentVerification", back_populates="contract")
    x402_payments = relationship("X402Payment", back_populates="contract")
    multi_chain_contracts = relationship("MultiChainContract", back_populates="contract")


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
    failure_paths = relationship("FailurePath", back_populates="simulation")
    intent_verifications = relationship("IntentVerification", back_populates="simulation")


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
    simulation = relationship("SimulationResult", back_populates="failure_paths")


class IntentVerification(Base):
    __tablename__ = "intent_verifications"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    request_id = Column(Integer, ForeignKey("ai_requests.id"), nullable=True)
    
    # Intent vs Behavior
    documented_intent = Column(Text)  # README/comments/NatSpec
    actual_behavior = Column(Text)  # What code actually does
    intent_match_score = Column(Integer)  # 0-100, how well they align
    intent_findings = Column(JSON)  # List of mismatches
    
    # Hidden Logic Detection
    hidden_logic_detected = Column(Boolean, default=False)
    dead_code_areas = Column(JSON)  # Lines of unused code
    delayed_execution_logic = Column(JSON)  # Logic that executes later
    conditional_activation = Column(JSON)  # Conditionally active code
    
    # Malicious Pattern Fingerprinting
    malicious_patterns_found = Column(Boolean, default=False)
    rug_pull_indicators = Column(JSON)  # List of rug-pull patterns
    honeypot_indicators = Column(JSON)  # List of honeypot patterns
    malicious_risk_score = Column(Integer)  # 0-100
    
    overall_trust_score = Column(Integer)  # 0-100
    ai_recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("Contract", foreign_keys=[contract_id])
    user = relationship("User", foreign_keys=[user_id])
    request = relationship("AIRequest", foreign_keys=[request_id])
    simulation = relationship("SimulationResult", back_populates="intent_verifications")
    hidden_logic_details = relationship("HiddenLogicDetail", back_populates="intent_verification")
    malicious_patterns = relationship("MaliciousPattern", back_populates="intent_verification")


class HiddenLogicDetail(Base):
    __tablename__ = "hidden_logic_details"

    id = Column(Integer, primary_key=True, index=True)
    intent_verification_id = Column(Integer, ForeignKey("intent_verifications.id"))
    logic_type = Column(String)  # dead_code, delayed_execution, conditional
    description = Column(Text)
    location = Column(String)  # Function/contract area where found
    line_numbers = Column(JSON)
    risk_level = Column(String)  # critical, high, medium, low, informational
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    intent_verification = relationship("IntentVerification", back_populates="hidden_logic_details")


class MaliciousPattern(Base):
    __tablename__ = "malicious_patterns"

    id = Column(Integer, primary_key=True, index=True)
    intent_verification_id = Column(Integer, ForeignKey("intent_verifications.id"))
    pattern_type = Column(String)  # rug_pull, honeypot, etc
    pattern_name = Column(String)  # e.g., "liquidity_lock_bypass", "unfair_tax"
    description = Column(Text)
    indicators = Column(JSON)  # Array of indicators found
    affected_functions = Column(JSON)
    severity = Column(String)  # critical, high, medium, low
    ai_reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    intent_verification = relationship("IntentVerification", back_populates="malicious_patterns")


class X402Payment(Base):
    __tablename__ = "x402_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    
    # Payment details
    transaction_hash = Column(String, unique=True, index=True)
    network = Column(String)  # solana, solana-devnet, base, polygon, etc
    amount_lamports = Column(Integer)  # For Solana: 1 SOL = 1,000,000,000 lamports
    amount_usd = Column(Float, nullable=True)
    payer_address = Column(String, index=True)
    receiver_address = Column(String)
    
    # Payment status and access control
    payment_status = Column(String, default="pending")  # pending, confirmed, failed, refunded
    tier = Column(String)  # free, basic, pro, enterprise
    access_level = Column(Integer)  # 0=free, 1=basic, 2=pro, 3=enterprise
    features_unlocked = Column(JSON)  # List of unlocked features
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # For subscription-based access
    
    user = relationship("User", foreign_keys=[user_id])
    contract = relationship("Contract", foreign_keys=[contract_id])
    access_logs = relationship("X402AccessLog", back_populates="payment")


class X402Subscription(Base):
    __tablename__ = "x402_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Subscription details
    tier = Column(String)  # basic, pro, enterprise
    recurring_payment_hash = Column(String, nullable=True)
    network = Column(String)  # solana, solana-devnet, base, polygon, etc
    
    # Pricing
    monthly_price_lamports = Column(Integer)
    monthly_price_usd = Column(Float, nullable=True)
    
    # Status
    status = Column(String, default="active")  # active, paused, cancelled
    next_billing_date = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    
    # Features included
    features = Column(JSON)  # List of features available
    api_calls_limit = Column(Integer, default=10000)
    monthly_calls_used = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id])
    payments = relationship("X402Payment", foreign_keys="X402Subscription.id")


class X402AccessLog(Base):
    __tablename__ = "x402_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("x402_payments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Access details
    endpoint = Column(String)  # e.g., /api/verify/intent, /api/simulate/failure-paths
    feature_accessed = Column(String)
    request_type = Column(String)  # analyze, optimize, simulate, verify
    
    # Request details
    tokens_used = Column(Integer, nullable=True)
    execution_time_ms = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    payment = relationship("X402Payment", back_populates="access_logs")
    user = relationship("User", foreign_keys=[user_id])


class MultiChainContract(Base):
    """Extended contract model for multi-chain support"""
    __tablename__ = "multi_chain_contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), index=True)
    
    # Multi-chain details
    blockchain = Column(Enum(Blockchain), index=True)
    language = Column(Enum(SmartContractLanguage))
    contract_address = Column(String, nullable=True, index=True)
    
    # Language-specific metadata
    abi_json = Column(JSON, nullable=True)  # For EVM contracts
    idl_json = Column(JSON, nullable=True)  # For Solana IDL
    move_module_name = Column(String, nullable=True)  # For Move contracts
    
    # Analysis metadata
    bytecode = Column(Text, nullable=True)
    deployment_tx = Column(String, nullable=True)
    compiler_version = Column(String, nullable=True)
    optimization_enabled = Column(Boolean, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    contract = relationship("Contract", foreign_keys=[contract_id])
    move_analysis = relationship("MoveLanguageAnalysis", back_populates="multi_chain_contract", cascade="all, delete-orphan")
    cosmwasm_analysis = relationship("CosmwasmAnalysis", back_populates="multi_chain_contract", cascade="all, delete-orphan")
    teal_analysis = relationship("TEALAnalysis", back_populates="multi_chain_contract", cascade="all, delete-orphan")
    circuit_analysis = relationship("CircuitAnalysis", back_populates="multi_chain_contract", cascade="all, delete-orphan")


class MoveLanguageAnalysis(Base):
    """Analysis results for Move language (Aptos/Sui)"""
    __tablename__ = "move_language_analysis"

    id = Column(Integer, primary_key=True, index=True)
    multi_chain_contract_id = Column(Integer, ForeignKey("multi_chain_contracts.id"))
    request_id = Column(Integer, ForeignKey("ai_requests.id"), nullable=True)
    
    # Move-specific analysis
    modules_found = Column(JSON)  # List of module names
    abilities_used = Column(JSON)  # copy, drop, store, key
    resource_patterns = Column(JSON)  # Identified resource patterns
    type_parameters = Column(JSON)  # Generic type usage
    
    # Move safety concerns
    safety_issues = Column(JSON)
    reentrancy_risks = Column(JSON)
    resource_leaks_found = Column(Boolean, default=False)
    
    findings = Column(JSON)
    risk_score = Column(Integer, nullable=True)
    ai_insights = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    multi_chain_contract = relationship("MultiChainContract", back_populates="move_analysis")
    request = relationship("AIRequest", foreign_keys=[request_id])


class CosmwasmAnalysis(Base):
    """Analysis results for CosmWasm (Cosmos ecosystem)"""
    __tablename__ = "cosmwasm_analysis"

    id = Column(Integer, primary_key=True, index=True)
    multi_chain_contract_id = Column(Integer, ForeignKey("multi_chain_contracts.id"))
    request_id = Column(Integer, ForeignKey("ai_requests.id"), nullable=True)
    
    # CosmWasm-specific analysis
    entry_points = Column(JSON)  # instantiate, execute, query, migrate, reply
    message_types = Column(JSON)  # ExecuteMsg, QueryMsg, etc.
    state_structure = Column(JSON)  # Contract state layout
    cw_standards_used = Column(JSON)  # CW20, CW721, etc.
    
    # Cosmos-specific concerns
    ibc_integration = Column(Boolean, default=False)
    cross_chain_risks = Column(JSON)
    state_consistency_issues = Column(JSON)
    
    findings = Column(JSON)
    risk_score = Column(Integer, nullable=True)
    ai_insights = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    multi_chain_contract = relationship("MultiChainContract", back_populates="cosmwasm_analysis")
    request = relationship("AIRequest", foreign_keys=[request_id])


class TEALAnalysis(Base):
    """Analysis results for TEAL/PyTeal (Algorand)"""
    __tablename__ = "teal_analysis"

    id = Column(Integer, primary_key=True, index=True)
    multi_chain_contract_id = Column(Integer, ForeignKey("multi_chain_contracts.id"))
    request_id = Column(Integer, ForeignKey("ai_requests.id"), nullable=True)
    
    # TEAL-specific analysis
    is_stateful = Column(Boolean)
    is_stateless = Column(Boolean)
    global_state_keys = Column(JSON)
    local_state_keys = Column(JSON)
    abi_methods = Column(JSON)
    
    # Algorand-specific concerns
    stack_depth_issues = Column(JSON)
    transaction_group_risks = Column(JSON)
    inner_transaction_usage = Column(JSON)
    atomic_transaction_safety = Column(JSON)
    
    findings = Column(JSON)
    risk_score = Column(Integer, nullable=True)
    ai_insights = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    multi_chain_contract = relationship("MultiChainContract", back_populates="teal_analysis")
    request = relationship("AIRequest", foreign_keys=[request_id])


class CircuitAnalysis(Base):
    """Analysis results for zkSNARK/Circuit verification"""
    __tablename__ = "circuit_analysis"

    id = Column(Integer, primary_key=True, index=True)
    multi_chain_contract_id = Column(Integer, ForeignKey("multi_chain_contracts.id"))
    request_id = Column(Integer, ForeignKey("ai_requests.id"), nullable=True)
    
    # Circuit analysis
    circuit_framework = Column(String)  # circom, noir, halo2, plonk, etc
    number_of_constraints = Column(Integer, nullable=True)
    number_of_signals = Column(Integer, nullable=True)
    number_of_public_inputs = Column(Integer, nullable=True)
    
    # ZK-specific security
    soundness_issues = Column(JSON)  # Potential soundness flaws
    completeness_verified = Column(Boolean, nullable=True)
    witness_generation_safety = Column(JSON)
    trusted_setup_requirements = Column(JSON)
    
    # Proof system analysis
    proof_system_type = Column(String)  # groth16, plonk, snark, stark, etc
    verification_key_analysis = Column(JSON)
    
    findings = Column(JSON)
    risk_score = Column(Integer, nullable=True)
    ai_insights = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    multi_chain_contract = relationship("MultiChainContract", back_populates="circuit_analysis")
    request = relationship("AIRequest", foreign_keys=[request_id])
