import os
import uuid
import pandas as pd
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query

from app.agents.data_inspector import inspect_dataset
from app.models.database import save_dataset_record, get_dataset_record, list_all_datasets
from app.services.dataset_service import load_dataset_dataframe
from app.utils.data_cleaning import sanitize_for_json

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.tsv'}

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), sheet_name: Optional[str] = Form(None)):
    """
    Accepts arbitrary dataset upload (CSV, XLSX, XLS, JSON, TSV).
    Profiles dataset dynamically using Data Inspector Agent.
    Zero domain hardcoding.
    """
    filename = file.filename
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Profile dataset dynamically
        profile = inspect_dataset(str(file_path), sheet_name=sheet_name)
        profile["file_name"] = filename  # Preserve display filename
        dataset_id = profile["id"]

        save_dataset_record(
            dataset_id=dataset_id,
            file_name=filename,
            file_path=str(file_path),
            file_type=ext.replace('.', '').upper(),
            file_size_bytes=len(content),
            profile_dict=profile
        )

        return profile
    except Exception as e:
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing dataset: {str(e)}")

@router.get("")
def get_datasets():
    """
    Lists all uploaded datasets.
    """
    return list_all_datasets()

@router.get("/{dataset_id}/profile")
def get_profile(dataset_id: str, sheet_name: Optional[str] = None):
    """
    Gets dataset profile, optionally re-profiling for specific Excel sheet.
    """
    rec = get_dataset_record(dataset_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    
    if sheet_name and rec["profile"].get("active_sheet") != sheet_name:
        file_path = rec["file_path"]
        new_profile = inspect_dataset(file_path, sheet_name=sheet_name)
        new_profile["id"] = dataset_id
        new_profile["file_name"] = rec["file_name"]
        save_dataset_record(dataset_id, rec["file_name"], file_path, rec["file_type"], rec["file_size_bytes"], new_profile)
        return new_profile

    return rec["profile"]

@router.get("/{dataset_id}/preview")
def get_preview(
    dataset_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sheet_name: Optional[str] = None
):
    """
    Paginated, searchable data preview endpoint.
    """
    try:
        df, profile = load_dataset_dataframe(dataset_id, sheet_name=sheet_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    if search:
        search_lower = search.lower()
        mask = df.astype(str).apply(lambda row: row.str.lower().str.contains(search_lower).any(), axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df

    total_rows = len(filtered_df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    sliced_df = filtered_df.iloc[start_idx:end_idx]

    return {
        "page": page,
        "page_size": page_size,
        "total_rows": total_rows,
        "total_pages": (total_rows + page_size - 1) // page_size if page_size > 0 else 1,
        "columns": [str(c) for c in df.columns],
        "rows": sanitize_for_json(sliced_df.to_dict(orient="records"))
    }
