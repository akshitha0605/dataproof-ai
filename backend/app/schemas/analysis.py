from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AmbiguityOption(BaseModel):
    field_name: str
    sample_value: Optional[Any] = None
    description: str

class AmbiguityDetails(BaseModel):
    is_ambiguous: bool = False
    prompt_message: Optional[str] = None
    options: List[AmbiguityOption] = []

class AnalysisPlan(BaseModel):
    intent: str
    metrics: List[str] = []
    operations: List[str] = []
    group_by: List[str] = []
    filters: List[Dict[str, Any]] = []
    sort: Optional[Dict[str, Any]] = None
    time_dimension: Optional[str] = None
    required_columns: List[str] = []
    joins: List[Dict[str, Any]] = []
    answerable: bool = True
    reason: Optional[str] = None

class AnalysisRequest(BaseModel):
    dataset_ids: List[str]
    sheet_name: Optional[str] = None
    question: str
    selected_ambiguous_column: Optional[str] = None
    follow_up_context: Optional[Dict[str, Any]] = None

class EvidenceData(BaseModel):
    summary_text: str
    columns: List[str] = []
    rows: List[Dict[str, Any]] = []
    total_rows: int = 0

class ChartSeries(BaseModel):
    name: str
    data_key: str

class ChartData(BaseModel):
    chart_type: str  # bar, line, area, pie, scatter, kpi, none
    title: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    data: List[Dict[str, Any]] = []

class TraceStep(BaseModel):
    stage: str
    status: str  # done, pending, failed
    details: str
    timestamp: float

class AnalysisResponse(BaseModel):
    analysis_id: str
    dataset_ids: List[str]
    question: str
    status: str  # VERIFIED ✓, CANNOT DETERMINE, UNVERIFIED, ERROR
    answer: str
    verification_explanation: str
    evidence: Optional[EvidenceData] = None
    proof_code: Optional[str] = None
    execution_result: Optional[Any] = None
    chart: Optional[ChartData] = None
    trace_steps: List[TraceStep] = []
    ambiguity: Optional[AmbiguityDetails] = None
    cannot_determine_details: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    created_at: str
