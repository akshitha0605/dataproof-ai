import time
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.schemas.analysis import AnalysisRequest, AnalysisResponse, TraceStep, EvidenceData
from app.models.database import get_dataset_record, save_analysis_record, get_analysis_history
from app.services.dataset_service import load_dataset_dataframe
from app.agents.question_planner import plan_question
from app.agents.data_validator import validate_analysis_request
from app.agents.code_generator import generate_analysis_code
from app.services.execution_service import execute_generated_code
from app.agents.verifier import verify_execution
from app.services.chart_service import generate_chart_config
from app.utils.data_cleaning import sanitize_for_json

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_question(req: AnalysisRequest):
    """
    Main DATAPROOF AI Analysis Pipeline.
    Executes: Understand -> Plan -> Validate -> CodeGen -> Execute -> Verify -> Proof Package.
    Zero hardcoding.
    """
    start_time = time.perf_counter()
    analysis_id = str(uuid.uuid4())[:8]

    if not req.dataset_ids:
        raise HTTPException(status_code=400, detail="At least one dataset ID is required.")

    # 1. Load dataset profiles and dataframes
    dataset_profiles = []
    dataframes = []
    
    for did in req.dataset_ids:
        rec = get_dataset_record(did)
        if not rec:
            raise HTTPException(status_code=404, detail=f"Dataset '{did}' not found.")
        dataset_profiles.append(rec["profile"])
        
        df, _ = load_dataset_dataframe(did, sheet_name=req.sheet_name)
        dataframes.append(df)

    main_df = dataframes[0]
    trace_steps = []

    # Trace step 1: Dataset inspection
    trace_steps.append(TraceStep(
        stage="Understanding dataset",
        status="done",
        details=f"Inspected schema with {main_df.shape[0]} rows, {main_df.shape[1]} columns",
        timestamp=round(time.perf_counter() - start_time, 3)
    ))

    # Trace step 2: Question Planning
    plan = plan_question(req.question, dataset_profiles, follow_up_context=req.follow_up_context)
    trace_steps.append(TraceStep(
        stage="Planning question",
        status="done",
        details=f"Intent: {plan.intent} | Operations: {', '.join(plan.operations)}",
        timestamp=round(time.perf_counter() - start_time, 3)
    ))

    # Trace step 3: Data Validation & Ambiguity check
    validation_res = validate_analysis_request(plan, dataset_profiles, req.question, selected_column=req.selected_ambiguous_column)
    
    if not validation_res["valid"]:
        status = validation_res["status"]
        exec_time = (time.perf_counter() - start_time) * 1000.0
        
        if status == "AMBIGUOUS":
            trace_steps.append(TraceStep(
                stage="Validating available data",
                status="pending",
                details="Detected multiple matching columns for generic query. Requesting user selection.",
                timestamp=round(time.perf_counter() - start_time, 3)
            ))
            res = AnalysisResponse(
                analysis_id=analysis_id,
                dataset_ids=req.dataset_ids,
                question=req.question,
                status="AMBIGUOUS",
                answer="Multiple numerical columns match your question. Please select which field you would like to analyze.",
                verification_explanation="Pending column selection from user.",
                ambiguity=validation_res["ambiguity"],
                trace_steps=trace_steps,
                execution_time_ms=round(exec_time, 2),
                created_at=datetime.now().isoformat()
            )
            save_analysis_record(analysis_id, req.dataset_ids, req.question, "AMBIGUOUS", res.answer, "", None, res.model_dump())
            return res

        elif status == "CANNOT DETERMINE":
            trace_steps.append(TraceStep(
                stage="Validating available data",
                status="failed",
                details=f"Insufficient data: {validation_res['reason']}",
                timestamp=round(time.perf_counter() - start_time, 3)
            ))
            res = AnalysisResponse(
                analysis_id=analysis_id,
                dataset_ids=req.dataset_ids,
                question=req.question,
                status="CANNOT DETERMINE",
                answer=f"CANNOT DETERMINE: {validation_res['reason']}",
                verification_explanation="Refused to guess or hallucinate as required information is missing from dataset.",
                cannot_determine_details={
                    "reason": validation_res["reason"],
                    "missing_information": validation_res.get("missing_information", []),
                    "available_information": validation_res.get("available_information", [])
                },
                trace_steps=trace_steps,
                execution_time_ms=round(exec_time, 2),
                created_at=datetime.now().isoformat()
            )
            save_analysis_record(analysis_id, req.dataset_ids, req.question, "CANNOT DETERMINE", res.answer, "", None, res.model_dump())
            return res

    trace_steps.append(TraceStep(
        stage="Validating available data",
        status="done",
        details="Validated column availability and data type compatibility",
        timestamp=round(time.perf_counter() - start_time, 3)
    ))

    # Trace step 4: Code Generation
    proof_code = generate_analysis_code(req.question, plan, dataset_profiles)
    trace_steps.append(TraceStep(
        stage="Generating proof code",
        status="done",
        details="Generated deterministic Python/Pandas analysis code",
        timestamp=round(time.perf_counter() - start_time, 3)
    ))

    # Trace step 5: Safe Code Execution
    exec_result = execute_generated_code(proof_code, main_df)
    if not exec_result["success"]:
        trace_steps.append(TraceStep(
            stage="Executing analysis",
            status="failed",
            details=f"Execution error: {exec_result.get('error')}",
            timestamp=round(time.perf_counter() - start_time, 3)
        ))
        exec_time = (time.perf_counter() - start_time) * 1000.0
        res = AnalysisResponse(
            analysis_id=analysis_id,
            dataset_ids=req.dataset_ids,
            question=req.question,
            status="ERROR",
            answer=f"Code execution encountered an error: {exec_result.get('error')}",
            verification_explanation="Execution failed in security sandbox.",
            proof_code=proof_code,
            execution_result=exec_result,
            trace_steps=trace_steps,
            execution_time_ms=round(exec_time, 2),
            created_at=datetime.now().isoformat()
        )
        save_analysis_record(analysis_id, req.dataset_ids, req.question, "ERROR", res.answer, proof_code, exec_result, res.model_dump())
        return res

    trace_steps.append(TraceStep(
        stage="Executing analysis",
        status="done",
        details=f"Code executed cleanly in sandbox ({exec_result.get('execution_time_ms')}ms)",
        timestamp=round(time.perf_counter() - start_time, 3)
    ))

    # Trace step 6: Verification
    verifier_res = verify_execution(exec_result, plan, req.question, dataset_profiles)
    trace_steps.append(TraceStep(
        stage="Verifying result",
        status="done" if verifier_res["verified"] else "failed",
        details=verifier_res["explanation"],
        timestamp=round(time.perf_counter() - start_time, 3)
    ))

    # Trace step 7: Evidence & Chart Extraction
    result_payload = exec_result.get("result", {})
    answer_text = result_payload.get("answer_summary", "Analysis completed successfully.")
    
    evidence_rows = result_payload.get("evidence_table", [])
    evidence_cols = list(evidence_rows[0].keys()) if (isinstance(evidence_rows, list) and len(evidence_rows) > 0 and isinstance(evidence_rows[0], dict)) else []

    evidence_obj = EvidenceData(
        summary_text=f"Extracted {len(evidence_rows)} supporting records from execution",
        columns=evidence_cols,
        rows=sanitize_for_json(evidence_rows),
        total_rows=len(evidence_rows)
    )

    chart_obj = generate_chart_config(result_payload, req.question)

    total_exec_time = (time.perf_counter() - start_time) * 1000.0

    res = AnalysisResponse(
        analysis_id=analysis_id,
        dataset_ids=req.dataset_ids,
        question=req.question,
        status=verifier_res["status"],
        answer=answer_text,
        verification_explanation=verifier_res["explanation"],
        evidence=evidence_obj,
        proof_code=proof_code,
        execution_result=sanitize_for_json(result_payload),
        chart=chart_obj,
        trace_steps=trace_steps,
        execution_time_ms=round(total_exec_time, 2),
        created_at=datetime.now().isoformat()
    )

    save_analysis_record(
        analysis_id=analysis_id,
        dataset_ids=req.dataset_ids,
        question=req.question,
        status=res.status,
        answer=res.answer,
        proof_code=proof_code,
        execution_result=res.execution_result,
        full_response_dict=res.model_dump()
    )

    return res

@router.get("/analysis-history")
def get_history(limit: int = Query(20, ge=1, le=100)):
    """
    Returns recent analysis history.
    """
    return get_analysis_history(limit=limit)
