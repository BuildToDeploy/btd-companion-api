from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_manager
from app.models import User, Contract
from app.schemas import ContractCreate, ContractResponse
from app.auth import verify_api_key
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.post("/", response_model=ContractResponse)
async def create_contract(
    contract: ContractCreate,
    user: User = Depends(verify_api_key),
    session: AsyncSession = Depends(db_manager.get_session),
):
    """Create a new contract"""
    db_contract = Contract(
        user_id=user.id,
        name=contract.name,
        source_code=contract.source_code,
        network=contract.network,
    )
    session.add(db_contract)
    await session.commit()
    await session.refresh(db_contract)
    logger.info(f"Contract created: {db_contract.id} for user {user.id}")
    return db_contract


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    user: User = Depends(verify_api_key),
    session: AsyncSession = Depends(db_manager.get_session),
):
    """Get contract by ID"""
    result = await session.execute(
        select(Contract).filter(
            Contract.id == contract_id,
            Contract.user_id == user.id
        )
    )
    contract = result.scalars().first()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )
    
    return contract


@router.get("/", response_model=list[ContractResponse])
async def list_contracts(
    user: User = Depends(verify_api_key),
    session: AsyncSession = Depends(db_manager.get_session),
):
    """List all contracts for user"""
    result = await session.execute(
        select(Contract).filter(Contract.user_id == user.id)
    )
    contracts = result.scalars().all()
    return contracts
