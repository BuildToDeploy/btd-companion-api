from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from datetime import datetime

from app.database import get_db
from app.models import (
    MultiChainContract, Contract, MoveLanguageAnalysis, CosmwasmAnalysis, 
    TEALAnalysis, CircuitAnalysis, User, AIRequest, Blockchain, SmartContractLanguage
)
from app.schemas import AnalysisRequest, AIProvider
from app.ai_providers import get_ai_provider
from app.parsers import MoveParser, CosmWasmParser, TEALParser, CircuitParser
import time

router = APIRouter(prefix="/api/multi-chain", tags=["multi-chain"])
logger = logging.getLogger(__name__)


@router.post("/contracts/move/analyze")
async def analyze_move_contract(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):
    """Analyze Move language contracts (Aptos/Sui)"""
    start_time = time.time()
    
    try:
        # Get contract source code
        source_code = request.source_code
        if request.contract_id and not source_code:
            contract = db.query(Contract).filter(Contract.id == request.contract_id).first()
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
            source_code = contract.source_code
        
        if not source_code:
            raise HTTPException(status_code=400, detail="No source code provided")
        
        # Parse Move code
        parser = MoveParser()
        modules = parser.parse_modules(source_code)
        resources = parser.extract_resources(source_code)
        patterns = parser.detect_resource_patterns(source_code)
        safety_issues = parser.detect_safety_issues(source_code)
        
        # Get AI analysis
        provider = get_ai_provider(request.provider)
        ai_response = await provider.analyze_contract(
            source_code,
            f"Analyze this Move smart contract for Aptos/Sui. Focus on resource safety, capability patterns, and Move-specific security issues.",
            request.provider
        )
        
        # Create or update analysis record
        if request.contract_id:
            # Create multi-chain contract record
            multi_chain = db.query(MultiChainContract).filter(
                MultiChainContract.contract_id == request.contract_id,
                MultiChainContract.blockchain == Blockchain.APTOS
            ).first()
            
            if not multi_chain:
                multi_chain = MultiChainContract(
                    contract_id=request.contract_id,
                    blockchain=Blockchain.APTOS,
                    language=SmartContractLanguage.MOVE
                )
                db.add(multi_chain)
                db.flush()
        
            # Create analysis record
            analysis = MoveLanguageAnalysis(
                multi_chain_contract_id=multi_chain.id,
                modules_found=[m["name"] for m in modules],
                abilities_used=patterns.get("capability_patterns", []),
                resource_patterns=[r["name"] for r in resources],
                safety_issues=safety_issues.get("unsafe_operations", []),
                risk_score=calculate_risk_score(safety_issues, ai_response),
                ai_insights=ai_response
            )
            db.add(analysis)
            db.commit()
        else:
            analysis = None
        
        execution_time = time.time() - start_time
        
        return {
            "blockchain": "aptos",
            "language": "move",
            "modules_found": modules,
            "resources": resources,
            "patterns": patterns,
            "safety_issues": safety_issues,
            "ai_insights": ai_response,
            "execution_time_ms": execution_time * 1000,
            "analysis_id": analysis.id if analysis else None
        }
    
    except Exception as e:
        logger.error(f"Error analyzing Move contract: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts/cosmwasm/analyze")
async def analyze_cosmwasm_contract(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):
    """Analyze CosmWasm contracts (Cosmos ecosystem)"""
    start_time = time.time()
    
    try:
        source_code = request.source_code
        if request.contract_id and not source_code:
            contract = db.query(Contract).filter(Contract.id == request.contract_id).first()
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
            source_code = contract.source_code
        
        # Parse CosmWasm code
        parser = CosmWasmParser()
        entry_points = parser.extract_entry_points(source_code)
        messages = parser.extract_messages(source_code)
        state_structure = parser.extract_state_structure(source_code)
        ibc_detected = parser.detect_ibc_integration(source_code)
        
        # Get AI analysis
        provider = get_ai_provider(request.provider)
        ai_response = await provider.analyze_contract(
            source_code,
            "Analyze this CosmWasm contract. Focus on message handling, state management, IBC integration, and Cosmos-specific security concerns.",
            request.provider
        )
        
        # Store analysis
        if request.contract_id:
            multi_chain = db.query(MultiChainContract).filter(
                MultiChainContract.contract_id == request.contract_id,
                MultiChainContract.blockchain == Blockchain.COSMOS
            ).first()
            
            if not multi_chain:
                multi_chain = MultiChainContract(
                    contract_id=request.contract_id,
                    blockchain=Blockchain.COSMOS,
                    language=SmartContractLanguage.COSMWASM
                )
                db.add(multi_chain)
                db.flush()
            
            analysis = CosmwasmAnalysis(
                multi_chain_contract_id=multi_chain.id,
                entry_points=entry_points,
                message_types=messages,
                state_structure=state_structure,
                ibc_integration=ibc_detected,
                risk_score=calculate_risk_score({"ibc": ibc_detected}, ai_response),
                ai_insights=ai_response
            )
            db.add(analysis)
            db.commit()
        else:
            analysis = None
        
        execution_time = time.time() - start_time
        
        return {
            "blockchain": "cosmos",
            "language": "cosmwasm",
            "entry_points": entry_points,
            "messages": messages,
            "state_structure": state_structure,
            "ibc_integration": ibc_detected,
            "ai_insights": ai_response,
            "execution_time_ms": execution_time * 1000,
            "analysis_id": analysis.id if analysis else None
        }
    
    except Exception as e:
        logger.error(f"Error analyzing CosmWasm contract: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts/teal/analyze")
async def analyze_teal_contract(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):
    """Analyze TEAL/PyTeal contracts (Algorand)"""
    start_time = time.time()
    
    try:
        source_code = request.source_code
        if request.contract_id and not source_code:
            contract = db.query(Contract).filter(Contract.id == request.contract_id).first()
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
            source_code = contract.source_code
        
        # Parse TEAL code
        parser = TEALParser()
        operations = parser.parse_teal_ops(source_code)
        state_schema = parser.detect_state_schema(source_code)
        security_issues = parser.detect_security_issues(source_code)
        
        # Get AI analysis
        provider = get_ai_provider(request.provider)
        ai_response = await provider.analyze_contract(
            source_code,
            "Analyze this TEAL smart contract for Algorand. Focus on stateful operations, transaction groups, stack depth, and Algorand-specific security patterns.",
            request.provider
        )
        
        # Store analysis
        if request.contract_id:
            multi_chain = db.query(MultiChainContract).filter(
                MultiChainContract.contract_id == request.contract_id,
                MultiChainContract.blockchain == Blockchain.ALGORAND
            ).first()
            
            if not multi_chain:
                multi_chain = MultiChainContract(
                    contract_id=request.contract_id,
                    blockchain=Blockchain.ALGORAND,
                    language=SmartContractLanguage.TEAL
                )
                db.add(multi_chain)
                db.flush()
            
            analysis = TEALAnalysis(
                multi_chain_contract_id=multi_chain.id,
                is_stateful=state_schema.get("is_stateful", False),
                is_stateless=not state_schema.get("is_stateful", False),
                global_state_keys=state_schema.get("global_state_ops", []),
                local_state_keys=state_schema.get("local_state_ops", []),
                abi_methods=state_schema.get("abi_methods", []),
                stack_depth_issues=security_issues.get("stack_depth_risks", []),
                transaction_group_risks=security_issues.get("txn_group_risks", []),
                risk_score=calculate_risk_score(security_issues, ai_response),
                ai_insights=ai_response
            )
            db.add(analysis)
            db.commit()
        else:
            analysis = None
        
        execution_time = time.time() - start_time
        
        return {
            "blockchain": "algorand",
            "language": "teal",
            "operations_count": len(operations),
            "state_schema": state_schema,
            "security_issues": security_issues,
            "ai_insights": ai_response,
            "execution_time_ms": execution_time * 1000,
            "analysis_id": analysis.id if analysis else None
        }
    
    except Exception as e:
        logger.error(f"Error analyzing TEAL contract: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: int,
    analysis_type: str,  # move, cosmwasm, teal, circuit
    db: Session = Depends(get_db),
):
    """Get analysis results for multi-chain contracts"""
    try:
        if analysis_type == "move":
            analysis = db.query(MoveLanguageAnalysis).filter(
                MoveLanguageAnalysis.id == analysis_id
            ).first()
        elif analysis_type == "cosmwasm":
            analysis = db.query(CosmwasmAnalysis).filter(
                CosmwasmAnalysis.id == analysis_id
            ).first()
        elif analysis_type == "teal":
            analysis = db.query(TEALAnalysis).filter(
                TEALAnalysis.id == analysis_id
            ).first()
        elif analysis_type == "circuit":
            analysis = db.query(CircuitAnalysis).filter(
                CircuitAnalysis.id == analysis_id
            ).first()
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "id": analysis.id,
            "type": analysis_type,
            "findings": analysis.findings,
            "risk_score": analysis.risk_score,
            "ai_insights": analysis.ai_insights,
            "created_at": analysis.created_at
        }
    
    except Exception as e:
        logger.error(f"Error fetching analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-blockchains")
async def get_supported_blockchains():
    """Get list of supported blockchains and languages"""
    return {
        "blockchains": [
            {
                "name": "Ethereum/EVM",
                "chains": ["ethereum", "polygon", "arbitrum", "base"],
                "languages": ["solidity", "vyper"]
            },
            {
                "name": "Aptos",
                "chains": ["aptos"],
                "languages": ["move"]
            },
            {
                "name": "Sui",
                "chains": ["sui"],
                "languages": ["move"]
            },
            {
                "name": "Cosmos",
                "chains": ["cosmos"],
                "languages": ["cosmwasm"]
            },
            {
                "name": "Algorand",
                "chains": ["algorand"],
                "languages": ["teal", "pyteal"]
            },
            {
                "name": "Solana",
                "chains": ["solana"],
                "languages": ["rust"]
            }
        ]
    }


def calculate_risk_score(issues: dict, ai_response: str) -> int:
    """Calculate risk score based on issues found and AI analysis"""
    base_score = 0
    
    # Count different types of issues
    total_issues = sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in issues.values())
    
    base_score = min(100, total_issues * 10)
    
    # Adjust based on severity keywords in AI response
    if "critical" in ai_response.lower():
        base_score = min(100, base_score + 30)
    elif "high" in ai_response.lower():
        base_score = min(100, base_score + 15)
    elif "medium" in ai_response.lower():
        base_score = min(100, base_score + 5)
    
    return base_score
