import re
import json
from typing import Dict, Any, List
from app.services.llm_service import call_gemini_api
from app.schemas.analysis import AnalysisPlan

def generate_analysis_code(question: str, plan: AnalysisPlan, dataset_profiles: List[Dict[str, Any]]) -> str:
    """
    Dynamically generates Python code operating on loaded DataFrame `df`.
    Zero hardcoding of dataset names or predefined answers.
    """
    schema_info = []
    for p in dataset_profiles:
        cols = [f"{c['name']} ({c['inferred_type']})" for c in p.get('columns', [])]
        schema_info.append(f"File: {p.get('file_name')} | Columns: {', '.join(cols)}")

    prompt = f"""You are a Python Data Analyst Code Generator.
Generate executable Python code operating on a pandas DataFrame `df`.

Discovered Schema:
{chr(10).join(schema_info)}

User Question: "{question}"
Analysis Plan:
- Intent: {plan.intent}
- Operations: {plan.operations}
- Metrics: {plan.metrics}
- Group By: {plan.group_by}
- Sort: {plan.sort}
- Required Columns: {plan.required_columns}

CRITICAL INSTRUCTIONS:
1. Generate MINIMAL, DETERMINISTIC Python code.
2. The code MUST store its final answer in a variable named `result`.
3. `result` MUST be a dictionary with keys:
   - "answer_summary": String explaining exact answer. FOR "WHO" / ENTITY QUESTIONS: Must return BOTH the entity name AND the value (e.g. "'Engineering' with 450,000").
   - "value": The result value or object. For "who" or entity questions, value MUST include BOTH entity name and value (e.g. "Engineering: 450,000" or {{"entity": "Engineering", "value": 450000}}).
   - "evidence_table": a list of dicts (e.g., df_result.head(20).to_dict(orient="records"))
   - "chart_type": "bar", "line", "pie", "scatter", "kpi", or "none"
   - "x_axis": column name for X-axis (or null)
   - "y_axis": column name for Y-axis (or null)
   - "operation": name of operation performed
4. Use ONLY standard libraries (pandas as pd, numpy as np, math, datetime).
5. DO NOT include fake numbers or hardcode results. Let pandas compute the numbers.
6. CRITICAL AGGREGATION RULE: When the user asks for 'average' or 'mean' (e.g. 'highest average', 'lowest mean', 'average by department'), you MUST aggregate using .mean() and MUST NOT use .sum().
7. Return ONLY executable Python code enclosed in ```python ... ``` or raw code.
"""

    llm_output = call_gemini_api(prompt)
    if llm_output:
        code_match = re.search(r'```python\s*(.*?)\s*```', llm_output, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        elif not llm_output.strip().startswith('{') and "result =" in llm_output:
            return llm_output.strip()

    # Dynamic Heuristic Code Generator Fallback
    return generate_heuristic_code(question, plan, dataset_profiles)

def generate_heuristic_code(question: str, plan: AnalysisPlan, dataset_profiles: List[Dict[str, Any]]) -> str:
    metric = plan.metrics[0] if plan.metrics else None
    group_col = plan.group_by[0] if plan.group_by else None
    ops = plan.operations or ["sum"]

    # Discover entity column if missing for 'who' / entity questions
    if not group_col and any(w in question.lower() for w in ["who", "which person", "which employee", "which department", "which category", "which student", "which vendor", "which client"]):
        for p in dataset_profiles:
            for c in p.get('columns', []):
                if c['inferred_type'] in ['categorical', 'text', 'string']:
                    group_col = c['name']
                    break
            if group_col:
                break

    code_lines = [
        "# Dynamically generated Pandas analysis code",
        "import pandas as pd",
        "import numpy as np",
        "",
        "# Ensure clean data working copy",
        "working_df = df.copy()",
        ""
    ]

    # Convert date column if needed
    if plan.time_dimension:
        code_lines.append(f"if '{plan.time_dimension}' in working_df.columns:")
        code_lines.append(f"    working_df['{plan.time_dimension}'] = pd.to_datetime(working_df['{plan.time_dimension}'], errors='coerce')")
        code_lines.append("")

    # If numeric metric column, clean it
    if metric:
        code_lines.append(f"if '{metric}' in working_df.columns:")
        code_lines.append(f"    working_df['{metric}'] = pd.to_numeric(working_df['{metric}'], errors='coerce')")
        code_lines.append("")

    is_avg = ("average" in ops or "mean" in ops or any(w in question.lower() for w in ["average", "mean", "avg"]))
    agg_func = "mean" if is_avg else "sum"
    agg_label = "average" if is_avg else "total"

    if group_col and metric:
        # Grouped metric analysis
        if "maximum" in ops or "ranking" in ops or any(w in question.lower() for w in ["highest", "max", "top", "best", "most", "who", "which"]):
            code_lines.extend([
                f"grouped = working_df.groupby('{group_col}')['{metric}'].{agg_func}().reset_index()",
                f"grouped = grouped.sort_values(by='{metric}', ascending=False)",
                "top_row = grouped.iloc[0]",
                f"top_group = str(top_row['{group_col}'])",
                f"top_val = float(top_row['{metric}'])",
                "",
                "result = {",
                f"    'answer_summary': f\"'{{top_group}}' with {{top_val:,.2f}} (highest {agg_label} {metric}).\",",
                "    'value': f\"{top_group}: {top_val:,.2f}\",",
                "    'evidence_table': grouped.head(15).to_dict(orient='records'),",
                "    'chart_type': 'bar',",
                f"    'x_axis': '{group_col}',",
                f"    'y_axis': '{metric}',",
                f"    'operation': 'highest_{agg_label}_by_group'",
                "}"
            ])
        elif "minimum" in ops or any(w in question.lower() for w in ["lowest", "min", "bottom", "least"]):
            code_lines.extend([
                f"grouped = working_df.groupby('{group_col}')['{metric}'].{agg_func}().reset_index()",
                f"grouped = grouped.sort_values(by='{metric}', ascending=True)",
                "bot_row = grouped.iloc[0]",
                f"bot_group = str(bot_row['{group_col}'])",
                f"bot_val = float(bot_row['{metric}'])",
                "",
                "result = {",
                f"    'answer_summary': f\"'{{bot_group}}' with {{bot_val:,.2f}} (lowest {agg_label} {metric}).\",",
                "    'value': f\"{bot_group}: {bot_val:,.2f}\",",
                "    'evidence_table': grouped.head(15).to_dict(orient='records'),",
                "    'chart_type': 'bar',",
                f"    'x_axis': '{group_col}',",
                f"    'y_axis': '{metric}',",
                f"    'operation': 'lowest_{agg_label}_by_group'",
                "}"
            ])
        elif "average" in ops:
            code_lines.extend([
                f"grouped = working_df.groupby('{group_col}')['{metric}'].mean().reset_index()",
                f"grouped = grouped.sort_values(by='{metric}', ascending=False)",
                "avg_val = float(grouped['" + metric + "'].mean())",
                "",
                "result = {",
                f"    'answer_summary': f\"Average {metric} calculated across groups of {group_col} (overall mean: {{avg_val:,.2f}}).\",",
                "    'value': avg_val,",
                "    'evidence_table': grouped.head(15).to_dict(orient='records'),",
                "    'chart_type': 'bar',",
                f"    'x_axis': '{group_col}',",
                f"    'y_axis': '{metric}',",
                "    'operation': 'average_by_group'",
                "}"
            ])
        else:
            code_lines.extend([
                f"grouped = working_df.groupby('{group_col}')['{metric}'].sum().reset_index()",
                f"grouped = grouped.sort_values(by='{metric}', ascending=False)",
                "total_val = float(grouped['" + metric + "'].sum())",
                "",
                "result = {",
                f"    'answer_summary': f\"Total {metric} grouped by {group_col} (overall total: {{total_val:,.2f}}).\",",
                "    'value': total_val,",
                "    'evidence_table': grouped.head(15).to_dict(orient='records'),",
                "    'chart_type': 'bar',",
                f"    'x_axis': '{group_col}',",
                f"    'y_axis': '{metric}',",
                "    'operation': 'sum_by_group'",
                "}"
            ])
    elif metric:
        # Aggregation over single metric column
        if "average" in ops or "mean" in ops:
            code_lines.extend([
                f"avg_val = float(working_df['{metric}'].mean())",
                "result = {",
                f"    'answer_summary': f\"The average of {metric} across all records is {{avg_val:,.2f}}.\",",
                "    'value': avg_val,",
                "    'evidence_table': working_df[['" + metric + "']].describe().reset_index().to_dict(orient='records'),",
                "    'chart_type': 'kpi',",
                "    'x_axis': None,",
                f"    'y_axis': '{metric}',",
                "    'operation': 'average'",
                "}"
            ])
        elif "maximum" in ops or "highest" in question.lower():
            code_lines.extend([
                f"max_val = float(working_df['{metric}'].max())",
                "result = {",
                f"    'answer_summary': f\"The maximum value for {metric} is {{max_val:,.2f}}.\",",
                "    'value': max_val,",
                "    'evidence_table': working_df.nlargest(10, '" + metric + "').to_dict(orient='records'),",
                "    'chart_type': 'kpi',",
                "    'x_axis': None,",
                f"    'y_axis': '{metric}',",
                "    'operation': 'maximum'",
                "}"
            ])
        elif "minimum" in ops or "lowest" in question.lower():
            code_lines.extend([
                f"min_val = float(working_df['{metric}'].min())",
                "result = {",
                f"    'answer_summary': f\"The minimum value for {metric} is {{min_val:,.2f}}.\",",
                "    'value': min_val,",
                "    'evidence_table': working_df.nsmallest(10, '" + metric + "').to_dict(orient='records'),",
                "    'chart_type': 'kpi',",
                "    'x_axis': None,",
                f"    'y_axis': '{metric}',",
                "    'operation': 'minimum'",
                "}"
            ])
        else:
            code_lines.extend([
                f"total_val = float(working_df['{metric}'].sum())",
                "result = {",
                f"    'answer_summary': f\"The overall total for {metric} is {{total_val:,.2f}}.\",",
                "    'value': total_val,",
                "    'evidence_table': [{'Metric': '" + metric + "', 'Total': total_val, 'Record_Count': len(working_df)}],",
                "    'chart_type': 'kpi',",
                "    'x_axis': None,",
                f"    'y_axis': '{metric}',",
                "    'operation': 'sum'",
                "}"
            ])
    elif group_col:
        # Grouped count
        code_lines.extend([
            f"counts = working_df['{group_col}'].value_counts().reset_index()",
            f"counts.columns = ['{group_col}', 'Record_Count']",
            "top_row = counts.iloc[0]",
            "top_cat = top_row['" + group_col + "']",
            "top_cnt = int(top_row['Record_Count'])",
            "result = {",
            f"    'answer_summary': f\"Category '{{top_cat}}' has the highest frequency with {{top_cnt}} records.\",",
            "    'value': top_cnt,",
            "    'evidence_table': counts.head(15).to_dict(orient='records'),",
            "    'chart_type': 'bar',",
            f"    'x_axis': '{group_col}',",
            "    'y_axis': 'Record_Count',",
            "    'operation': 'count_by_group'",
            "}"
        ])
    else:
        # General count or record overview
        code_lines.extend([
            "total_rows = len(working_df)",
            "result = {",
            "    'answer_summary': f'Dataset contains a total of {total_rows:,} records across {len(working_df.columns)} columns.',",
            "    'value': total_rows,",
            "    'evidence_table': working_df.head(10).to_dict(orient='records'),",
            "    'chart_type': 'kpi',",
            "    'x_axis': None,",
            "    'y_axis': 'Record_Count',",
            "    'operation': 'count'",
            "}"
        ])

    return "\n".join(code_lines)
