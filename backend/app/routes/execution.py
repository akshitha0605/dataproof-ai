from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.execution_service import execute_generated_code
from app.services.dataset_service import load_dataset_dataframe

router = APIRouter(prefix="/api", tags=["execution"])

class StandaloneExecuteRequest(BaseModel):
    dataset_id: str
    code: str
    sheet_name: Optional[str] = None

@router.post("/execute")
def standalone_execute(req: StandaloneExecuteRequest):
    """
    Executes Python code against specified dataset inside security sandbox.
    """
    try:
        df, _ = load_dataset_dataframe(req.dataset_id, sheet_name=req.sheet_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    exec_res = execute_generated_code(req.code, df)
    return exec_res
