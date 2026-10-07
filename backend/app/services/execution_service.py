import pandas as pd
from typing import Dict, Any
from app.utils.security import run_safe_code
from app.utils.data_cleaning import sanitize_for_json

def execute_generated_code(code_str: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes generated Python code on DataFrame `df` in isolated security sandbox.
    Returns clean JSON-serializable execution package.
    """
    context = {
        "df": df
    }

    raw_exec = run_safe_code(code_str, execution_context=context, timeout_seconds=10.0)

    if raw_exec["success"] and raw_exec.get("result"):
        raw_exec["result"] = sanitize_for_json(raw_exec["result"])

    return raw_exec
