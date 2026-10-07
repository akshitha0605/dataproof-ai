from typing import Dict, Any, List, Optional
from app.schemas.analysis import ChartData

def generate_chart_config(exec_result_dict: Dict[str, Any], question: str) -> Optional[ChartData]:
    """
    Dynamically generates chart configuration based on execution output shape and types.
    """
    if not exec_result_dict or not isinstance(exec_result_dict, dict):
        return None

    chart_type = exec_result_dict.get("chart_type", "none")
    x_col = exec_result_dict.get("x_axis")
    y_col = exec_result_dict.get("y_axis")
    evidence = exec_result_dict.get("evidence_table", [])

    if chart_type == "none" or not evidence or not isinstance(evidence, list):
        return None

    # Format chart title
    title = f"{question}"
    if x_col and y_col:
        title = f"{y_col} by {x_col}"
    elif y_col:
        title = f"Analysis of {y_col}"

    chart_data_rows = []
    for row in evidence[:20]: # top 20 points
        if isinstance(row, dict):
            chart_data_rows.append(row)

    if not chart_data_rows:
        return None

    return ChartData(
        chart_type=chart_type,
        title=title,
        x_axis=x_col,
        y_axis=y_col,
        data=chart_data_rows
    )
