from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_manager
from app.models import User, Contract, AIRequest, AnalysisResult, AIProvider
from app.schemas import AnalysisRequest, AnalysisResponse, SecurityFinding
from app.auth import verify_api_key
from app.ai_manager import ai_manager
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze-contract", response_model=AnalysisResponse)
async def analyze_contract(
    request: AnalysisRequest,
    user: User = Depends(verify_api_key),
    session: AsyncSession = Depends(db_manager.get_session),
):
    """Analyze smart contract for security vulnerabilities"""
    
    # Get contract source code
    if request.contract_id:
        result = await session.execute(
            select(Contract).filter(
                Contract.id == request.contract_id,
                Contract.user_id == user.id
            )
        )
        contract = result.scalars().first()
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found",
            )
        source_code = contract.source_code
    elif request.source_code:
        source_code = request.source_code
        contract = None
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either contract_id or source_code must be provided",
        )
    
    # Call AI provider
    try:
        analysis_result = await ai_manager.analyze_contract(source_code, request.provider)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )
    
    # Store request in database
    ai_request = AIRequest(
        user_id=user.id,
        contract_id=contract.id if contract else None,
        provider_used=request.provider,
        request_type="analyze",
        execution_time_ms=analysis_result["execution_time_ms"],
    )
    session.add(ai_request)
    await session.flush()
    
    # Store analysis result
    result_record = AnalysisResult(
        request_id=ai_request.id,
        contract_id=contract.id if contract else None,
        analysis_type="security",
        risk_score=analysis_result["risk_score"],
        findings=analysis_result["findings"],
        suggestions=[],
        raw_response=json.dumps(analysis_result),
    )
    session.add(result_record)
    await session.commit()
    
    logger.info(f"Contract analysis completed for user {user.id}")
    
    # Format findings
    findings = [
        SecurityFinding(
            severity=f.get("severity", "medium"),
            title=f.get("title", ""),
            description=f.get("description", ""),
        )
        for f in analysis_result.get("findings", [])
    ]
    
    return AnalysisResponse(
        security_findings=findings,
        risk_score=analysis_result["risk_score"],
        explanation=analysis_result["explanation"],
        execution_time_ms=analysis_result["execution_time_ms"],
        provider_used=request.provider,
    )
