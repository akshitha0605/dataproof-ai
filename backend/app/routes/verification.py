from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.agents.verifier import verify_execution
from app.schemas.analysis import AnalysisPlan

router = APIRouter(prefix="/api", tags=["verification"])

class StandaloneVerifyRequest(BaseModel):
    execution_result: Dict[str, Any]
    plan: AnalysisPlan
    question: str
    dataset_profiles: List[Dict[str, Any]] = []

@router.post("/verify")
def standalone_verify(req: StandaloneVerifyRequest):
    """
    Standalone endpoint to perform verification audit on an execution package.
    """
    res = verify_execution(req.execution_result, req.plan, req.question, req.dataset_profiles)
    return res
