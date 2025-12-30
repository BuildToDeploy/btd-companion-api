"""
x402 Payment Integration Routes
Handles Solana and multi-chain payments via x402 protocol
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.database import get_db
from app.models import X402Payment, X402Subscription, X402AccessLog, User, Contract, AIRequest
from app.schemas import (
    X402PaymentRequest, X402PaymentResponse, X402PaymentVerificationRequest,
    X402PaymentVerificationResponse, X402SubscriptionRequest, X402SubscriptionResponse,
    X402AccessLogResponse, X402SubscriptionTier
)
from datetime import datetime, timedelta
from typing import List
import httpx
from app.config import get_settings

router = APIRouter(prefix="/api/x402", tags=["x402-payments"])
settings = get_settings()

# Mapping of network to x402 API endpoint
X402_ENDPOINTS = {
    "solana": "https://api.x402.com/api/solana/paid-content",
    "solana-devnet": "https://api.x402.com/api/solana-devnet/paid-content",
    "base": "https://api.x402.com/api/base/paid-content",
    "base-sepolia": "https://api.x402.com/api/base-sepolia/paid-content",
    "polygon": "https://api.x402.com/api/polygon/paid-content",
    "polygon-amoy": "https://api.x402.com/api/polygon-amoy/paid-content",
    "xlayer": "https://api.x402.com/api/xlayer/paid-content",
    "xlayer-testnet": "https://api.x402.com/api/xlayer-testnet/paid-content",
    "peaq": "https://api.x402.com/api/peaq/paid-content",
    "sei": "https://api.x402.com/api/sei/paid-content",
    "sei-testnet": "https://api.x402.com/api/sei-testnet/paid-content",
}

# Tier definitions
TIERS = {
    "free": {
        "price_lamports": 0,
        "price_usd": 0,
        "features": ["basic_analysis", "limited_simulations"],
        "api_calls_limit": 100,
        "priority_support": False,
        "description": "Free tier with basic features"
    },
    "basic": {
        "price_lamports": 5000000,  # 0.005 SOL
        "price_usd": 0.50,
        "features": ["contract_analysis", "simulations", "intent_verification"],
        "api_calls_limit": 10000,
        "priority_support": False,
        "description": "Basic tier for regular users"
    },
    "pro": {
        "price_lamports": 50000000,  # 0.05 SOL
        "price_usd": 5.00,
        "features": ["contract_analysis", "simulations", "intent_verification", "malicious_detection", "priority_queue"],
        "api_calls_limit": 100000,
        "priority_support": True,
        "description": "Pro tier for advanced users"
    },
    "enterprise": {
        "price_lamports": 500000000,  # 0.5 SOL
        "price_usd": 50.00,
        "features": ["all_features", "custom_analysis", "api_access", "priority_queue", "dedicated_support"],
        "api_calls_limit": 1000000,
        "priority_support": True,
        "description": "Enterprise tier with full access"
    }
}


@router.get("/tiers", response_model=List[X402SubscriptionTier])
async def get_subscription_tiers():
    """Get available subscription tiers"""
    return [
        X402SubscriptionTier(
            tier=tier,
            monthly_price_lamports=config["price_lamports"],
            monthly_price_usd=config["price_usd"],
            features=config["features"],
            api_calls_limit=config["api_calls_limit"],
            priority_support=config["priority_support"],
            description=config["description"]
        )
        for tier, config in TIERS.items()
    ]


@router.post("/payment/initiate", response_model=dict)
async def initiate_payment(
    payment_request: X402PaymentRequest,
    current_user: User = Depends(get_db),  # This should be replaced with proper auth
    db: AsyncSession = Depends(get_db)
):
    """Initiate a x402 payment"""
    
    if payment_request.network not in X402_ENDPOINTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Network {payment_request.network} not supported"
        )
    
    if payment_request.tier not in TIERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tier {payment_request.tier} not supported"
        )
    
    # Create payment record
    payment = X402Payment(
        user_id=current_user.id,
        contract_id=payment_request.contract_id,
        network=payment_request.network,
        amount_lamports=payment_request.amount_lamports,
        payer_address="",  # Will be set after payment
        receiver_address=settings.x402_receiver_address,
        tier=payment_request.tier,
        access_level=list(TIERS.keys()).index(payment_request.tier),
        features_unlocked=TIERS[payment_request.tier]["features"],
        payment_status="pending"
    )
    
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    
    # Return payment initiation URL for x402 protocol
    return {
        "payment_id": payment.id,
        "network": payment_request.network,
        "amount_lamports": payment_request.amount_lamports,
        "tier": payment_request.tier,
        "x402_url": X402_ENDPOINTS[payment_request.network],
        "message": "Redirect user to x402_url to complete payment"
    }


@router.post("/payment/verify", response_model=X402PaymentVerificationResponse)
async def verify_payment(
    verification: X402PaymentVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify and confirm a x402 payment"""
    
    # Query for existing payment
    result = await db.execute(
        select(X402Payment).where(
            X402Payment.transaction_hash == verification.transaction_hash
        )
    )
    payment = result.scalars().first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify with x402 API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{X402_ENDPOINTS[verification.network]}/verify",
                json={"transaction_hash": verification.transaction_hash},
                timeout=10
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment verification failed with x402 service"
                )
            
            tx_data = response.json()
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify with x402: {str(e)}"
            )
    
    # Update payment status
    payment.payment_status = "confirmed"
    payment.transaction_hash = verification.transaction_hash
    payment.confirmed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(payment)
    
    return X402PaymentVerificationResponse(
        is_valid=True,
        status="confirmed",
        confirmed_at=payment.confirmed_at,
        tier=payment.tier,
        access_level=payment.access_level,
        message="Payment verified and confirmed"
    )


@router.post("/subscription/create", response_model=X402SubscriptionResponse)
async def create_subscription(
    sub_request: X402SubscriptionRequest,
    current_user: User = Depends(get_db),  # Replace with proper auth
    db: AsyncSession = Depends(get_db)
):
    """Create a recurring subscription"""
    
    if sub_request.tier not in TIERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tier {sub_request.tier} not supported"
        )
    
    tier_config = TIERS[sub_request.tier]
    
    subscription = X402Subscription(
        user_id=current_user.id,
        tier=sub_request.tier,
        network=sub_request.network,
        monthly_price_lamports=tier_config["price_lamports"],
        monthly_price_usd=tier_config["price_usd"],
        status="active",
        auto_renew=sub_request.auto_renew,
        next_billing_date=datetime.utcnow() + timedelta(days=30),
        features=tier_config["features"],
        api_calls_limit=tier_config["api_calls_limit"]
    )
    
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    return X402SubscriptionResponse.from_orm(subscription)


@router.get("/subscription/current", response_model=X402SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_db),  # Replace with proper auth
    db: AsyncSession = Depends(get_db)
):
    """Get current user subscription"""
    
    result = await db.execute(
        select(X402Subscription).where(
            X402Subscription.user_id == current_user.id,
            X402Subscription.status == "active"
        ).order_by(X402Subscription.created_at.desc())
    )
    subscription = result.scalars().first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return X402SubscriptionResponse.from_orm(subscription)


@router.post("/access/log")
async def log_access(
    payment_id: int,
    endpoint: str,
    feature: str,
    tokens_used: int,
    execution_time_ms: float,
    current_user: User = Depends(get_db),  # Replace with proper auth
    db: AsyncSession = Depends(get_db)
):
    """Log feature access for usage tracking"""
    
    access_log = X402AccessLog(
        payment_id=payment_id,
        user_id=current_user.id,
        endpoint=endpoint,
        feature_accessed=feature,
        tokens_used=tokens_used,
        execution_time_ms=execution_time_ms,
        success=True
    )
    
    db.add(access_log)
    await db.commit()
    await db.refresh(access_log)
    
    return X402AccessLogResponse.from_orm(access_log)


@router.get("/access/history", response_model=List[X402AccessLogResponse])
async def get_access_history(
    current_user: User = Depends(get_db),  # Replace with proper auth
    db: AsyncSession = Depends(get_db),
    limit: int = 100
):
    """Get user's access history"""
    
    result = await db.execute(
        select(X402AccessLog)
        .where(X402AccessLog.user_id == current_user.id)
        .order_by(X402AccessLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return [X402AccessLogResponse.from_orm(log) for log in logs]
