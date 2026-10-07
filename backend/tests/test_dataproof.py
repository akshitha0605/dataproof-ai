import os
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.agents.data_inspector import inspect_dataset
from app.agents.question_planner import plan_question
from app.agents.data_validator import validate_analysis_request
from app.agents.code_generator import generate_analysis_code
from app.services.execution_service import execute_generated_code
from app.agents.verifier import verify_execution
from app.utils.security import run_safe_code, validate_code_security

client = TestClient(app)

TEST_DIR = Path(__file__).parent / "tmp_test_files"

@pytest.fixture(autouse=True)
def setup_tmp_files():
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    yield

def test_1_csv_upload_and_profiling():
    csv_file = TEST_DIR / "unknown_sensors_99.csv"
    df = pd.DataFrame({
        "Sensor_Code": ["S-101", "S-102", "S-103", "S-104"],
        "Pressure_PSI": [14.7, 22.4, 18.9, 31.0],
        "Vibration_Hz": [120, 150, 95, 210]
    })
    df.to_csv(csv_file, index=False)

    with open(csv_file, "rb") as f:
        response = client.post("/api/datasets/upload", files={"file": ("unknown_sensors_99.csv", f, "text/csv")})

    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "unknown_sensors_99.csv"
    assert data["row_count"] == 4
    assert data["column_count"] == 3
    assert data["quality_status"] in ["Excellent", "Good"]

def test_2_xlsx_upload_and_multi_sheet():
    xlsx_file = TEST_DIR / "multi_dept.xlsx"
    with pd.ExcelWriter(xlsx_file, engine="openpyxl") as writer:
        pd.DataFrame({"Dept": ["HR", "IT"], "Headcount": [5, 20]}).to_excel(writer, sheet_name="Overview", index=False)
        pd.DataFrame({"Dept": ["HR", "IT"], "Budget": [50000, 200000]}).to_excel(writer, sheet_name="Finances", index=False)

    with open(xlsx_file, "rb") as f:
        response = client.post("/api/datasets/upload", files={"file": ("multi_dept.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})

    assert response.status_code == 200
    data = response.json()
    assert "Overview" in data["sheets"]
    assert "Finances" in data["sheets"]

def test_3_json_upload():
    json_file = TEST_DIR / "log_records.json"
    df = pd.DataFrame({"log_id": [1, 2], "level": ["INFO", "ERROR"]})
    df.to_json(json_file, orient="records")

    with open(json_file, "rb") as f:
        response = client.post("/api/datasets/upload", files={"file": ("log_records.json", f, "application/json")})

    assert response.status_code == 200
    data = response.json()
    assert data["row_count"] == 2

def test_4_dangerous_code_rejection():
    dangerous_code_1 = "import os; os.system('echo HACKED')"
    is_safe, err = validate_code_security(dangerous_code_1)
    assert not is_safe
    assert "blocked for security" in err

    dangerous_code_2 = "eval('1 + 1')"
    is_safe, err = validate_code_security(dangerous_code_2)
    assert not is_safe
    assert "forbidden" in err

    res = run_safe_code(dangerous_code_1, execution_context={})
    assert not res["success"]
    assert "Security Violation" in res["error"]

def test_5_cannot_determine_for_missing_information():
    profile = {
        "file_name": "inventory.csv",
        "columns": [
            {"name": "Product", "inferred_type": "text"},
            {"name": "Price", "inferred_type": "float"}
        ]
    }
    
    plan = plan_question("What is the average employee salary?", [profile])
    validation = validate_analysis_request(plan, [profile], "What is the average employee salary?")
    
    assert not validation["valid"]
    assert validation["status"] == "CANNOT DETERMINE"

def test_6_ambiguous_question_handling():
    profile = {
        "file_name": "finances.csv",
        "columns": [
            {"name": "Revenue", "inferred_type": "float", "sample_values": [1000]},
            {"name": "Expenditure", "inferred_type": "float", "sample_values": [500]},
            {"name": "Net_Profit", "inferred_type": "float", "sample_values": [500]}
        ]
    }
    
    plan = plan_question("What is the highest value?", [profile])
    validation = validate_analysis_request(plan, [profile], "What is the highest value?")
    
    assert not validation["valid"]
    assert validation["status"] == "AMBIGUOUS"
    assert validation["ambiguity"].is_ambiguous
    assert len(validation["ambiguity"].options) == 3

def test_7_unknown_dataset_and_unknown_question_real_execution():
    path = TEST_DIR / "galaxy_star_metrics.csv"
    df = pd.DataFrame({
        "Star_System_Name": ["Alpha Centauri", "Betelgeuse", "Sirius", "Vega"],
        "Luminosity_Index": [1.5, 12000.0, 25.4, 40.1],
        "Distance_LightYears": [4.37, 642.5, 8.6, 25.0]
    })
    df.to_csv(path, index=False)

    with open(path, "rb") as f:
        up_resp = client.post("/api/datasets/upload", files={"file": ("galaxy_star_metrics.csv", f, "text/csv")})
    
    dataset_id = up_resp.json()["id"]

    analysis_resp = client.post("/api/analyze", json={
        "dataset_ids": [dataset_id],
        "question": "Which Star System Name has the maximum Luminosity Index?"
    })

    assert analysis_resp.status_code == 200
    res = analysis_resp.json()
    
    print("\nTEST 7 DETAILED RESPONSE:", res)
    assert res["status"] == "VERIFIED ✓", f"Expected VERIFIED ✓ but got {res['status']}: {res['answer']}"
    assert "Betelgeuse" in res["answer"] or "12,000" in res["answer"] or "12000" in res["answer"]
    assert res["proof_code"] is not None
    assert res["execution_result"] is not None
    assert res["evidence"]["total_rows"] > 0
