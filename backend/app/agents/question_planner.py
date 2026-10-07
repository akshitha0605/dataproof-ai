import json
import re
from typing import List, Dict, Any
from app.services.llm_service import call_gemini_api
from app.schemas.analysis import AnalysisPlan

def plan_question(question: str, dataset_profiles: List[Dict[str, Any]], follow_up_context: Dict[str, Any] = None) -> AnalysisPlan:
    """
    Transforms natural-language question into a structured analysis plan JSON.
    Zero hardcoded dataset schemas or domain-specific names.
    """
    schema_summary = []
    available_cols = []
    numeric_cols = []
    categorical_cols = []
    datetime_cols = []

    for profile in dataset_profiles:
        file_info = f"Dataset File: {profile.get('file_name')} (Sheet: {profile.get('active_sheet', 'Default')})"
        col_list = []
        for col in profile.get('columns', []):
            cname = col['name']
            ctype = col['inferred_type']
            col_list.append(f"{cname} ({ctype})")
            available_cols.append(cname)
            if ctype in ['integer', 'float', 'currency', 'percentage']:
                numeric_cols.append(cname)
            elif ctype in ['categorical', 'boolean', 'text']:
                categorical_cols.append(cname)
            elif ctype in ['datetime']:
                datetime_cols.append(cname)
        schema_summary.append(f"{file_info}\nColumns: {', '.join(col_list)}")

    prompt = f"""You are an expert AI Data Analyst Planner.
Analyze the following natural-language user question against the discovered dataset schema.

{chr(10).join(schema_summary)}

User Question: "{question}"
Follow-Up Context: {json.dumps(follow_up_context) if follow_up_context else "None"}

Generate a structured JSON analysis plan with exact column names present in the dataset schema.
Schema output format:
{{
    "intent": "Brief description of analysis goal",
    "metrics": ["list of numerical metric columns"],
    "operations": ["sum", "average", "maximum", "minimum", "count", "distinct_count", "ranking", "grouping", "filtering", "date_trend", "correlation", "outlier"],
    "group_by": ["list of categorical/date grouping columns"],
    "filters": [],
    "sort": {{"field": "column_name", "ascending": false}},
    "time_dimension": "datetime column if applicable or null",
    "required_columns": ["exact column names required"],
    "joins": [],
    "answerable": true,
    "reason": null
}}

If the question asks for information that cannot be derived from the available columns, set "answerable": false and explain in "reason".
DO NOT calculate numbers or hallucinate column names. Use ONLY actual discovered columns.
Return ONLY valid JSON.
"""

    llm_output = call_gemini_api(prompt)
    if llm_output:
        try:
            clean_str = re.sub(r'^```json\s*', '', llm_output.strip())
            clean_str = re.sub(r'```$', '', clean_str).strip()
            parsed = json.loads(clean_str)
            return AnalysisPlan(**parsed)
        except Exception:
            pass

    return generate_fallback_plan(question, available_cols, numeric_cols, categorical_cols, datetime_cols, follow_up_context)

def generate_fallback_plan(question: str, available_cols: list, numeric_cols: list, categorical_cols: list, datetime_cols: list, follow_up_context: dict = None) -> AnalysisPlan:
    q_lower = question.lower().strip()
    q_words = set(re.findall(r'\w+', q_lower))
    
    prev_group_by = follow_up_context.get("group_by", []) if follow_up_context else []
    prev_metrics = follow_up_context.get("metrics", []) if follow_up_context else []

    operations = []
    group_by = []
    metrics = []
    time_dimension = datetime_cols[0] if datetime_cols else None

    # Detect Operations dynamically
    if any(w in q_lower for w in ["total", "sum", "overall", "amount"]):
        operations.append("sum")
    if any(w in q_lower for w in ["average", "mean", "avg"]):
        operations.append("average")
    if any(w in q_lower for w in ["highest", "maximum", "max", "top", "best", "most"]):
        operations.append("maximum")
        operations.append("ranking")
    if any(w in q_lower for w in ["lowest", "minimum", "min", "bottom", "worst", "least"]):
        operations.append("minimum")
        operations.append("ranking")
    if any(w in q_lower for w in ["count", "how many", "number of", "total records"]):
        operations.append("count")
    if any(w in q_lower for w in ["duplicate", "duplicates"]):
        operations.append("outlier")
    if any(w in q_lower for w in ["trend", "over time", "monthly", "yearly", "daily", "by month", "by year"]):
        operations.append("date_trend")
    if any(w in q_lower for w in ["compare", "by ", "per ", "each ", "distribution", "breakdown"]):
        operations.append("grouping")

    if not operations:
        operations = ["sum" if numeric_cols else "count"]

    # Match numeric metric columns by fuzzy token matching
    for col in numeric_cols:
        col_words = set(re.findall(r'\w+', col.lower()))
        if col_words and col_words.intersection(q_words):
            metrics.append(col)

    # Match categorical grouping columns
    for col in categorical_cols + datetime_cols:
        col_words = set(re.findall(r'\w+', col.lower()))
        if col_words and col_words.intersection(q_words):
            group_by.append(col)

    # Standard English filler, operations & analytical synonym stopwords
    stopwords = {
        "what", "is", "are", "was", "were", "has", "have", "had", "does", "do", "did",
        "the", "a", "an", "of", "to", "for", "in", "on", "at", "by", "from", "with",
        "which", "where", "who", "how", "many", "show", "find", "get", "give", "tell", "me",
        "list", "top", "bottom", "best", "worst", "maximum", "minimum", "total", "average",
        "overall", "sum", "count", "record", "records", "value", "values", "item", "items",
        "amount", "number", "figure", "figures", "data", "dataset", "highest", "lowest",
        "max", "min", "most", "least", "mean", "avg"
    }

    unmatched_query_nouns = [w for w in q_words if w not in stopwords and len(w) > 2]
    
    col_tokens = set()
    for col in available_cols:
        col_tokens.update(re.findall(r'\w+', col.lower()))

    unmatched_concept = None
    for noun in unmatched_query_nouns:
        if not any(noun in token or token in noun for token in col_tokens):
            unmatched_concept = noun
            break

    if unmatched_concept and not metrics and not group_by:
        return AnalysisPlan(
            intent="Unanswerable missing concept request",
            required_columns=[unmatched_concept],
            answerable=False,
            reason=f"The dataset does not contain any column related to '{unmatched_concept}'."
        )

    if not metrics and prev_metrics:
        metrics = prev_metrics
    elif not metrics and numeric_cols and not unmatched_concept:
        metrics = [numeric_cols[0]]

    if not group_by and prev_group_by:
        group_by = prev_group_by
    elif not group_by and categorical_cols:
        if "who" in q_words or any(w in q_lower for w in ["which person", "which employee", "which department", "which category", "which student", "who has", "who is", "who had"]):
            entity_col = None
            for col in categorical_cols:
                clow = col.lower()
                if any(k in clow for k in ["name", "emp", "person", "dept", "department", "student", "user", "rep", "vendor", "client", "category", "author", "type", "team"]):
                    entity_col = col
                    break
            if not entity_col:
                entity_col = categorical_cols[0]
            group_by = [entity_col]

    required_columns = list(dict.fromkeys(metrics + group_by))

    sort_dict = None
    if "maximum" in operations or "highest" in q_lower:
        sort_dict = {"field": metrics[0] if metrics else (available_cols[0] if available_cols else ""), "ascending": False}
    elif "minimum" in operations or "lowest" in q_lower:
        sort_dict = {"field": metrics[0] if metrics else (available_cols[0] if available_cols else ""), "ascending": True}

    return AnalysisPlan(
        intent=f"Analyze {question}",
        metrics=metrics,
        operations=operations,
        group_by=group_by,
        filters=[],
        sort=sort_dict,
        time_dimension=time_dimension,
        required_columns=required_columns,
        answerable=True,
        reason=None
    )
