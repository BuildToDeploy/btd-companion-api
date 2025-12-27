from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_manager
from app.models import User, Contract, AIRequest, AnalysisResult, AIProvider
from app.schemas import OptimizationRequest, OptimizationResponse, OptimizationSuggestion
from app.auth import verify_api_key
from app.ai_manager import ai_manager
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["optimization"])


@router.post("/optimize-contract", response_model=OptimizationResponse)
async def optimize_contract(
    request: OptimizationRequest,
    user: User = Depends(verify_api_key),
    session: AsyncSession = Depends(db_manager.get_session),
):
    """Get gas optimization suggestions for contract"""
    
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
        optimization_result = await ai_manager.optimize_contract(source_code, request.provider)
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}",
        )
    
    # Store request in database
    ai_request = AIRequest(
        user_id=user.id,
        contract_id=contract.id if contract else None,
        provider_used=request.provider,
        request_type="optimize",
        execution_time_ms=optimization_result["execution_time_ms"],
    )
    session.add(ai_request)
    await session.flush()
    
    # Store result
    result_record = AnalysisResult(
        request_id=ai_request.id,
        contract_id=contract.id if contract else None,
        analysis_type="optimization",
        risk_score=None,
        findings=[],
        suggestions=optimization_result["suggestions"],
        raw_response=json.dumps(optimization_result),
    )
    session.add(result_record)
    await session.commit()
    
    logger.info(f"Contract optimization completed for user {user.id}")
    
    # Format suggestions
    suggestions = [
        OptimizationSuggestion(
            area=s.get("area", ""),
            suggestion=s.get("suggestion", ""),
            potential_savings=s.get("potential_savings"),
        )
        for s in optimization_result.get("suggestions", [])
    ]
    
    return OptimizationResponse(
        suggestions=suggestions,
        execution_time_ms=optimization_result["execution_time_ms"],
        provider_used=request.provider,
    )
