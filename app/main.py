from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import db_manager
from app.config import get_settings
from app.routes import contracts, analysis, optimization, deployment, monitoring, simulation, intent_verification, x402_payments
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown"""
    logger.info("Starting BTD Companion backend...")
    await db_manager.init()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down BTD Companion backend...")
    await db_manager.close()


def create_app() -> FastAPI:
    """Create and configure FastAPI app"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="Web3 AI Developer Platform Backend",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(contracts.router)
    app.include_router(analysis.router)
    app.include_router(optimization.router)
    app.include_router(deployment.router)
    app.include_router(monitoring.router)
    app.include_router(simulation.router)
    app.include_router(intent_verification.router)
    app.include_router(x402_payments.router)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": settings.app_name}
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
