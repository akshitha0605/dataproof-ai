from typing import Dict, Any, List, Optional
from app.schemas.analysis import AnalysisPlan, AmbiguityDetails, AmbiguityOption

def validate_analysis_request(plan: AnalysisPlan, dataset_profiles: List[Dict[str, Any]], question: str, selected_column: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates whether the planned question can be cleanly executed on the uploaded dataset.
    Detects ambiguity and unanswerable questions.
    """
    all_columns = []
    numeric_cols = []
    categorical_cols = []
    col_type_map = {}

    for profile in dataset_profiles:
        for col in profile.get('columns', []):
            cname = col['name']
            ctype = col['inferred_type']
            all_columns.append(cname)
            col_type_map[cname] = ctype
            if ctype in ['integer', 'float', 'currency', 'percentage']:
                numeric_cols.append(cname)
            elif ctype in ['categorical', 'boolean', 'text', 'datetime']:
                categorical_cols.append(cname)

    # 1. Check if plan is marked unanswerable by planner
    if not plan.answerable:
        return {
            "valid": False,
            "status": "CANNOT DETERMINE",
            "reason": plan.reason or "The required information is not available in the dataset.",
            "missing_information": plan.required_columns or ["Requested metric/attribute"],
            "available_information": all_columns,
            "ambiguity": None
        }

    q_lower = question.lower().strip()

    # 2. Check AMBIGUITY
    # If question asks for "highest value", "total", "average", "maximum", "minimum" without specifying a column
    # and multiple numeric columns exist, and user hasn't selected one:
    generic_intents = ["highest value", "maximum value", "total value", "average value", "lowest value", "minimum value", "what is the total", "what is the highest", "what is the average", "show top"]
    is_generic_q = any(g in q_lower for g in generic_intents) or (len(plan.metrics) > 1 and not any(m.lower() in q_lower for m in plan.metrics))
    
    if (is_generic_q or not plan.metrics) and len(numeric_cols) > 1 and not selected_column:
        options = []
        for nc in numeric_cols:
            # find sample value
            sample_val = None
            for p in dataset_profiles:
                for col in p.get('columns', []):
                    if col['name'] == nc and col.get('sample_values'):
                        sample_val = col['sample_values'][0]
            options.append(AmbiguityOption(
                field_name=nc,
                sample_value=sample_val,
                description=f"Analyze numeric column '{nc}'"
            ))

        ambiguity_details = AmbiguityDetails(
            is_ambiguous=True,
            prompt_message=f"I found multiple numerical fields ({', '.join(numeric_cols)}). Which field would you like me to analyze?",
            options=options
        )
        return {
            "valid": False,
            "status": "AMBIGUOUS",
            "reason": "Multiple numerical columns found for generic query.",
            "ambiguity": ambiguity_details
        }

    # If user selected an ambiguous column explicitly:
    if selected_column and selected_column in all_columns:
        plan.metrics = [selected_column]
        if selected_column not in plan.required_columns:
            plan.required_columns.append(selected_column)

    # 3. Check column existence
    missing_cols = [c for c in plan.required_columns if c not in all_columns]
    if missing_cols:
        return {
            "valid": False,
            "status": "CANNOT DETERMINE",
            "reason": f"Required dataset columns {missing_cols} are missing.",
            "missing_information": missing_cols,
            "available_information": all_columns,
            "ambiguity": None
        }

    # 4. Check type compatibility (e.g. sum on text column)
    for metric in plan.metrics:
        m_type = col_type_map.get(metric, 'text')
        if m_type not in ['integer', 'float', 'currency', 'percentage'] and any(op in plan.operations for op in ['sum', 'average', 'mean']):
            return {
                "valid": False,
                "status": "CANNOT DETERMINE",
                "reason": f"Cannot perform numerical calculation ({', '.join(plan.operations)}) on non-numeric column '{metric}' (type: {m_type}).",
                "missing_information": [f"Numeric data type for column '{metric}'"],
                "available_information": numeric_cols,
                "ambiguity": None
            }

    return {
        "valid": True,
        "status": "VALID",
        "reason": "Validation passed successfully.",
        "ambiguity": None
    }
