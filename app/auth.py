from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_manager
from app.models import User, APIKey
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def verify_api_key(credentials: HTTPAuthCredentials = Depends(security), session: AsyncSession = Depends(db_manager.get_session)) -> User:
    """Verify API key and return user"""
    api_key = credentials.credentials
    
    # Query for API key
    result = await session.execute(
        select(APIKey).filter(APIKey.key == api_key, APIKey.is_active == True)
    )
    api_key_record = result.scalars().first()
    
    if not api_key_record:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    result = await session.execute(
        select(User).filter(User.id == api_key_record.user_id, User.is_active == True)
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last_used timestamp
    api_key_record.last_used = db_manager.AsyncSessionLocal.get_bind().func.now()
    await session.commit()
    
    return user
