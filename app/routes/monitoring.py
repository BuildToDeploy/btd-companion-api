from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_manager
from app.models import User, Contract, Monitoring
from app.schemas import MonitoringResponse
from app.auth import verify_api_key
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["monitoring"])


@router.get("/monitor/{contract_address}", response_model=MonitoringResponse)
async def get_monitoring_data(
    contract_address: str,
    user: User = Depends(verify_api_key),
    session: AsyncSession = Depends(db_manager.get_session),
):
    """Fetch monitoring data for contract"""
    
    # Get contract
    result = await session.execute(
        select(Contract).filter(
            Contract.address == contract_address,
            Contract.user_id == user.id
        )
    )
    contract = result.scalars().first()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )
    
    # Get monitoring data
    result = await session.execute(
        select(Monitoring).filter(Monitoring.contract_id == contract.id)
    )
    monitoring = result.scalars().first()
    
    if not monitoring:
        # Create initial monitoring record
        monitoring = Monitoring(
            contract_id=contract.id,
            last_checked=datetime.utcnow(),
            status="active",
            events_count=0,
        )
        session.add(monitoring)
        await session.commit()
    
    logger.info(f"Monitoring data retrieved for contract {contract_address}")
    
    return MonitoringResponse(
        contract_id=monitoring.contract_id,
        status=monitoring.status,
        last_checked=monitoring.last_checked,
        events_count=monitoring.events_count,
    )
