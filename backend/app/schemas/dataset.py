from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ColumnProfile(BaseModel):
    name: str
    inferred_type: str  # integer, float, categorical, datetime, boolean, identifier, text, currency, percentage
    missing_count: int
    missing_percentage: float
    unique_count: int
    sample_values: List[Any]
    stats: Optional[Dict[str, Any]] = None

class DatasetProfile(BaseModel):
    id: str
    file_name: str
    file_type: str
    file_size_bytes: int
    row_count: int
    column_count: int
    sheets: List[str] = []
    active_sheet: Optional[str] = None
    columns: List[ColumnProfile]
    quality_score: int
    quality_status: str  # Excellent, Good, Needs Attention, Poor
    quality_issues: List[str] = []
    sample_rows: List[Dict[str, Any]] = []
    created_at: str

class DatasetSummary(BaseModel):
    id: str
    file_name: str
    file_type: str
    row_count: int
    column_count: int
    quality_status: str
    created_at: str
