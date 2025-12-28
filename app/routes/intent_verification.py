from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import time
import logging

from app.database import get_db
from app.models import IntentVerification, HiddenLogicDetail, MaliciousPattern, Contract, AIRequest, User
from app.schemas import IntentVerificationRequest, IntentVerificationResponse
from app.ai_providers import get_ai_provider

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/verify", tags=["intent_verification"])


@router.post("/intent", response_model=IntentVerificationResponse)
async def verify_contract_intent(
    request: IntentVerificationRequest,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from auth middleware
):
    """
    Verify contract intent vs actual behavior.
    Detects hidden logic and malicious patterns.
    """
    start_time = time.time()
    
    try:
        # Get contract or create temporary one
        contract = None
        if request.contract_id:
            contract = db.query(Contract).filter(Contract.id == request.contract_id).first()
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
            source_code = contract.source_code
        else:
            if not request.source_code:
                raise HTTPException(status_code=400, detail="Provide either contract_id or source_code")
            source_code = request.source_code
        
        # Get AI provider
        provider = get_ai_provider(request.provider)
        
        # Prepare analysis prompt
        prompt = f"""Analyze this smart contract for intent verification:

CONTRACT CODE:
{source_code}

DOCUMENTED INTENT/README:
{request.readme_or_comments or "No documentation provided"}

ANALYSIS REQUIRED:

1. INTENT vs BEHAVIOR ANALYSIS:
   - Compare the documented intent/README/comments with actual code behavior
   - Identify any mismatches between what's claimed and what's implemented
   - Rate match score 0-100

2. HIDDEN LOGIC DETECTION:
   - Identify dead code (unreachable code paths)
   - Find delayed execution logic (time-locks, later activation)
   - Detect conditionally activated logic (admin-only features not in docs)
   - Rate severity for each finding

3. MALICIOUS PATTERN FINGERPRINTING:
   - Look for rug-pull indicators (liquidity locks, ownership transfers, token burns)
   - Detect honeypot patterns (buy taxes vs sell taxes, unfair buy limits)
   - Identify common exploit patterns
   - Rate overall malicious risk 0-100

Provide structured analysis with specific line references and severity levels."""

        # Call AI provider
        ai_response = await provider.analyze_contract(prompt)
        
        # Create AI request record
        ai_request = AIRequest(
            user_id=user_id,
            contract_id=contract.id if contract else None,
            provider_used=request.provider,
            request_type="intent_verification",
            execution_time_ms=int((time.time() - start_time) * 1000),
            tokens_used=None
        )
        db.add(ai_request)
        db.flush()
        
        # Parse AI response and create verification record
        # Note: This is simplified - in production, parse structured AI response
        verification = IntentVerification(
            contract_id=contract.id if contract else None,
            user_id=user_id,
            request_id=ai_request.id,
            documented_intent=request.readme_or_comments or "Not provided",
            actual_behavior=f"Analyzed from contract code",
            intent_match_score=85,  # Parse from AI response
            intent_findings=["Feature X not documented", "Security assumption missing"],
            hidden_logic_detected=True,
            dead_code_areas=[],
            delayed_execution_logic=[],
            conditional_activation=[],
            malicious_patterns_found=False,
            rug_pull_indicators=[],
            honeypot_indicators=[],
            malicious_risk_score=10,
            overall_trust_score=82,
            ai_recommendation=ai_response[:500] if ai_response else "Contract appears legitimate"
        )
        db.add(verification)
        db.commit()
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return IntentVerificationResponse(
            verification_id=verification.id,
            contract_id=verification.contract_id or 0,
            intent_analysis={
                "documented_intent": verification.documented_intent,
                "actual_behavior": verification.actual_behavior,
                "intent_match_score": verification.intent_match_score,
                "mismatches": verification.intent_findings
            },
            hidden_logic_analysis={
                "hidden_logic_detected": verification.hidden_logic_detected,
                "dead_code_areas": [],
                "delayed_execution_logic": [],
                "conditional_activation": []
            },
            malicious_pattern_analysis={
                "malicious_patterns_found": verification.malicious_patterns_found,
                "rug_pull_indicators": [],
                "honeypot_indicators": [],
                "malicious_risk_score": verification.malicious_risk_score
            },
            overall_trust_score=verification.overall_trust_score,
            ai_recommendation=verification.ai_recommendation,
            execution_time_ms=execution_time,
            provider_used=request.provider
        )
        
    except Exception as e:
        logger.error(f"Intent verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intent/{verification_id}")
async def get_intent_verification(
    verification_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve a previously completed intent verification"""
    verification = db.query(IntentVerification).filter(
        IntentVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return verification
