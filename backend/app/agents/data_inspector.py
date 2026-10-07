import pandas as pd
import numpy as np
import os
import json
import uuid
import re
from datetime import datetime
from pathlib import Path

from app.utils.data_cleaning import sanitize_for_json

def inspect_dataset(file_path: str, sheet_name: str = None) -> dict:
    """
    Dynamically profiles any supported dataset file (CSV, XLSX, XLS, JSON, TSV).
    Zero dataset-specific hardcoding.
    """
    path = Path(file_path)
    file_ext = path.suffix.lower()
    file_name = path.name
    file_size_bytes = path.stat().st_size

    sheets = []
    active_sheet = None
    df = None

    # Load dataframe dynamically based on format
    if file_ext in ['.xlsx', '.xls']:
        with pd.ExcelFile(file_path) as excel_file:
            sheets = excel_file.sheet_names
            active_sheet = sheet_name if (sheet_name and sheet_name in sheets) else (sheets[0] if sheets else None)
            if active_sheet:
                df = pd.read_excel(excel_file, sheet_name=active_sheet)
            else:
                df = pd.read_excel(excel_file)
    elif file_ext == '.tsv':
        df = pd.read_csv(file_path, sep='\t')
    elif file_ext == '.json':
        try:
            df = pd.read_json(file_path)
        except Exception:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.json_normalize(data)
    elif file_ext == '.csv':
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

    row_count, column_count = df.shape

    columns_profile = []
    quality_issues = []

    total_cells = row_count * column_count if (row_count > 0 and column_count > 0) else 1
    total_missing_cells = int(df.isna().sum().sum())
    missing_cell_pct = (total_missing_cells / total_cells) * 100.0 if total_cells > 0 else 0

    duplicate_rows = int(df.duplicated().sum()) if row_count > 0 else 0
    duplicate_pct = (duplicate_rows / row_count) * 100.0 if row_count > 0 else 0

    empty_cols = [str(col) for col in df.columns if df[col].isna().all()]
    empty_cols_pct = (len(empty_cols) / column_count) * 100.0 if column_count > 0 else 0

    if missing_cell_pct > 15:
        quality_issues.append(f"High missing value rate: {missing_cell_pct:.1f}% of total cells missing")
    if duplicate_rows > 0:
        quality_issues.append(f"Dataset contains {duplicate_rows} duplicate rows ({duplicate_pct:.1f}%)")
    if empty_cols:
        quality_issues.append(f"{len(empty_cols)} columns are completely empty: {', '.join(empty_cols[:3])}")

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_percentage = round((missing_count / row_count) * 100.0, 2) if row_count > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))

        non_null_series = series.dropna()

        # Inferred type detection
        inferred_type = infer_column_type(series, non_null_series, str(col), row_count)

        stats = {}
        if inferred_type in ['integer', 'float', 'currency', 'percentage']:
            numeric_vals = pd.to_numeric(non_null_series, errors='coerce').dropna()
            if not numeric_vals.empty:
                stats = {
                    "min": sanitize_for_json(numeric_vals.min()),
                    "max": sanitize_for_json(numeric_vals.max()),
                    "mean": round(float(numeric_vals.mean()), 4),
                    "median": round(float(numeric_vals.median()), 4),
                    "std": round(float(numeric_vals.std()), 4) if len(numeric_vals) > 1 else 0.0
                }
        elif inferred_type in ['datetime']:
            date_vals = pd.to_datetime(non_null_series, errors='coerce').dropna()
            if not date_vals.empty:
                stats = {
                    "min_date": sanitize_for_json(date_vals.min()),
                    "max_date": sanitize_for_json(date_vals.max())
                }
        elif inferred_type in ['categorical', 'boolean', 'text']:
            val_counts = non_null_series.value_counts().head(5).to_dict()
            stats = {
                "top_frequencies": sanitize_for_json(val_counts)
            }

        sample_vals = sanitize_for_json(non_null_series.head(5).tolist())

        columns_profile.append({
            "name": str(col),
            "inferred_type": inferred_type,
            "missing_count": missing_count,
            "missing_percentage": missing_percentage,
            "unique_count": unique_count,
            "sample_values": sample_vals,
            "stats": stats
        })

    # Dynamic Quality Score calculation
    quality_score = max(0, min(100, int(round(100.0 - (missing_cell_pct * 0.4) - (duplicate_pct * 0.3) - (empty_cols_pct * 0.3)))))

    if quality_score >= 90:
        quality_status = "Excellent"
    elif quality_score >= 75:
        quality_status = "Good"
    elif quality_score >= 55:
        quality_status = "Needs Attention"
    else:
        quality_status = "Poor"

    sample_rows = sanitize_for_json(df.head(10).to_dict(orient="records"))
    dataset_id = str(uuid.uuid4())[:8]

    profile_dict = {
        "id": dataset_id,
        "file_name": file_name,
        "file_type": file_ext.replace('.', '').upper(),
        "file_size_bytes": file_size_bytes,
        "row_count": row_count,
        "column_count": column_count,
        "sheets": sheets,
        "active_sheet": active_sheet,
        "columns": columns_profile,
        "quality_score": quality_score,
        "quality_status": quality_status,
        "quality_issues": quality_issues,
        "sample_rows": sample_rows,
        "created_at": datetime.now().isoformat()
    }

    return profile_dict

def infer_column_type(series: pd.Series, non_null: pd.Series, col_name: str, total_rows: int) -> str:
    """
    Infers data type based on statistical features & sample values, not hardcoded column names.
    """
    if non_null.empty:
        return "text"

    # Check boolean
    unique_vals = set(non_null.unique())
    if unique_vals.issubset({True, False, 0, 1, 'True', 'False', 'true', 'false', 'YES', 'NO', 'Yes', 'No', 'y', 'n', 'Y', 'N'}):
        return "boolean"

    # Check numeric types safely
    if pd.api.types.is_numeric_dtype(series):
        if pd.api.types.is_integer_dtype(series) or (non_null % 1 == 0).all():
            if non_null.nunique() == len(non_null) and ("id" in col_name.lower() or "code" in col_name.lower()):
                return "identifier"
            return "integer"
        return "float"

    # Try string checks
    sample_str = [str(x).strip() for x in non_null.head(50)]
    
    # Check currency
    currency_pattern = re.compile(r'^[$\u20ac\u20b9\u00a3]?\s*-?\d+(?:,\d{3})*(?:\.\d+)?$')
    if all(currency_pattern.match(s) for s in sample_str if s):
        return "currency"

    # Check percentage
    if all(s.endswith('%') for s in sample_str if s):
        return "percentage"

    # Check date/datetime
    try:
        parsed = pd.to_datetime(non_null.head(30), format='mixed', errors='coerce')
        if parsed.notna().sum() > len(non_null.head(30)) * 0.7:
            return "datetime"
    except Exception:
        pass

    # Check categorical vs text/identifier
    unique_cnt = non_null.nunique()
    if unique_cnt <= 30 or (total_rows > 0 and (unique_cnt / total_rows) < 0.2):
        return "categorical"
    
    if unique_cnt == len(non_null) and total_rows > 5:
        return "identifier"

    return "text"
