import numpy as np
import pandas as pd
from datetime import date, datetime

def sanitize_for_json(obj):
    """
    Recursively convert pandas/numpy objects (NaN, NaT, int64, float64, Timestamps, arrays)
    into standard Python JSON-serializable types safely.
    """
    if obj is None:
        return None

    # Handle sequence/array types first before checking scalar nulls
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, np.ndarray):
        return [sanitize_for_json(v) for v in obj.tolist()]
    elif isinstance(obj, pd.Series):
        return [sanitize_for_json(v) for v in obj.to_list()]
    elif isinstance(obj, pd.DataFrame):
        return [sanitize_for_json(row) for row in obj.to_dict(orient="records")]
    elif isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}

    # Now handle scalars
    try:
        if pd.isna(obj):
            return None
    except Exception:
        pass

    if isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (pd.Timestamp, datetime, date)):
        return obj.isoformat()
    elif hasattr(obj, 'item'):
        return sanitize_for_json(obj.item())

    return str(obj)
