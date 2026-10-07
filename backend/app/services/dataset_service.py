import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from app.models.database import get_dataset_record

def load_dataset_dataframe(dataset_id: str, sheet_name: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads dataset file associated with dataset_id into a Pandas DataFrame.
    """
    rec = get_dataset_record(dataset_id)
    if not rec:
        raise ValueError(f"Dataset ID '{dataset_id}' not found.")

    file_path = rec["file_path"]
    file_type = rec["file_type"].lower()

    if file_type in ['xlsx', 'xls']:
        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names
        target_sheet = sheet_name if (sheet_name and sheet_name in sheets) else sheets[0]
        df = pd.read_excel(file_path, sheet_name=target_sheet)
    elif file_type == 'tsv':
        df = pd.read_csv(file_path, sep='\t')
    elif file_type == 'json':
        try:
            df = pd.read_json(file_path)
        except Exception:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.json_normalize(data)
    else:  # CSV
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')

    return df, rec["profile"]
