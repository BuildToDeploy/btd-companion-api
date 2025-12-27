from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_manager
from app.models import User, Contract, AIRequest, AnalysisResult, AIProvider
from app.schemas import DeploymentRequest, DeploymentResponse
from app.auth import verify_api_key
from app.ai_manager import ai_manager
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["deployment"])


@router.post("/deploy", response_model=DeploymentResponse)
async def validate_deployment(
    request: DeploymentRequest,
    user: User = Depends(verify_api_key),
    session: AsyncSession = Depends(db_manager.get_session),
):
    """Validate contract deployment configuration"""
    
    # Get contract
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
    
    # Validate network
    valid_networks = ["ethereum", "polygon", "arbitrum", "optimism", "base", "sepolia"]
    if request.network not in valid_networks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid network. Valid options: {', '.join(valid_networks)}",
        )
    
    # Call AI provider
    try:
        deployment_result = await ai_manager.validate_deployment(
            contract.source_code,
            request.network
        )
    except Exception as e:
        logger.error(f"Deployment validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment validation failed: {str(e)}",
        )
    
    # Store request in database
    ai_request = AIRequest(
        user_id=user.id,
        contract_id=contract.id,
        provider_used=AIProvider.OPENAI,  # Default for deployment
        request_type="deploy",
        execution_time_ms=deployment_result["execution_time_ms"],
    )
    session.add(ai_request)
    await session.flush()
    
    # Store result
    result_record = AnalysisResult(
        request_id=ai_request.id,
        contract_id=contract.id,
        analysis_type="deployment",
        risk_score=None,
        findings=[],
        suggestions=deployment_result.get("warnings", []),
        raw_response=json.dumps(deployment_result),
    )
    session.add(result_record)
    await session.commit()
    
    logger.info(f"Deployment validation completed for user {user.id}, network: {request.network}")
    
    return DeploymentResponse(
        is_valid=deployment_result["is_valid"],
        network=request.network,
        estimated_gas=deployment_result.get("estimated_gas"),
        warnings=deployment_result.get("warnings", []),
        execution_time_ms=deployment_result["execution_time_ms"],
    )
