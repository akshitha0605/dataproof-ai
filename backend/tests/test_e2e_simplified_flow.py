import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_e2e_workflow():
    # 1. Upload sample CSV file
    csv_content = b"Department,Budget,Expenditure,Year\nEngineering,500000,450000,2023\nMarketing,300000,320000,2023\nSales,400000,380000,2023\n"
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_budget.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200, response.text
    profile = response.json()
    assert profile["file_name"] == "test_budget.csv"
    assert profile["row_count"] == 3
    dataset_id = profile["id"]

    # 2. Ask question: "Which department has the highest expenditure?"
    analyze_resp = client.post(
        "/api/analyze",
        json={
            "dataset_ids": [dataset_id],
            "question": "Which department has the highest expenditure?"
        }
    )
    assert analyze_resp.status_code == 200, analyze_resp.text
    data = analyze_resp.json()
    
    assert data["status"] == "VERIFIED ✓"
    assert "Engineering" in data["answer"] or "450,000" in data["answer"] or "450000" in data["answer"]
    assert data["proof_code"] is not None
    assert "import pandas" in data["proof_code"]
    assert data["evidence"] is not None
    assert len(data["evidence"]["rows"]) > 0

def test_who_question_returns_entity_and_value():
    # Upload CSV with Employee and Sales
    csv_content = b"Employee,Sales\nAlice,95000\nBob,72000\nCharlie,88000\n"
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_sales.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    dataset_id = response.json()["id"]

    # Ask "Who" question: "Who has the highest sales?"
    analyze_resp = client.post(
        "/api/analyze",
        json={
            "dataset_ids": [dataset_id],
            "question": "Who has the highest sales?"
        }
    )
    assert analyze_resp.status_code == 200, analyze_resp.text
    data = analyze_resp.json()

    assert data["status"] == "VERIFIED ✓"
    answer_text = str(data["answer"])
    
    # Must contain BOTH the entity ("Alice") AND the value ("95" / "95,000" / "95000")
    assert "Alice" in answer_text, f"Entity 'Alice' missing from answer: {answer_text}"
    assert "95" in answer_text or "95,000" in answer_text or "95000" in answer_text, f"Value '95000' missing from answer: {answer_text}"

def test_highest_average_aggregation_uses_mean_not_sum():
    # Upload student marks dataset
    csv_content = b"Department,Programming\nCS,90\nCS,100\nEE,80\nEE,70\nME,60\nME,50\n"
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_marks.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    dataset_id = response.json()["id"]

    # Ask: "Which department has the highest average Programming marks?"
    analyze_resp = client.post(
        "/api/analyze",
        json={
            "dataset_ids": [dataset_id],
            "question": "Which department has the highest average Programming marks?"
        }
    )
    assert analyze_resp.status_code == 200, analyze_resp.text
    data = analyze_resp.json()

    assert data["status"] == "VERIFIED ✓"
    proof_code = data["proof_code"]
    
    # MUST use .mean() for aggregation and MUST NOT use .sum()
    assert ".mean()" in proof_code, f"Code does not use .mean(): {proof_code}"
    assert ".sum()" not in proof_code, f"Code incorrectly uses .sum(): {proof_code}"

    # Department CS has mean 95.0, EE has mean 75.0, ME has mean 55.0
    answer_text = str(data["answer"])
    assert "CS" in answer_text, f"Expected department 'CS' in answer: {answer_text}"
    assert "95" in answer_text, f"Expected mean '95' in answer: {answer_text}"

def test_cannot_determine_workflow():
    # Upload CSV without salary column
    csv_content = b"Name,Role\nAlice,Engineer\nBob,Designer\n"
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_employees.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    dataset_id = response.json()["id"]

    # Ask question about salary: "What is the average salary?"
    analyze_resp = client.post(
        "/api/analyze",
        json={
            "dataset_ids": [dataset_id],
            "question": "What is the average salary?"
        }
    )
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert data["status"] == "CANNOT DETERMINE"
    assert "does not contain" in data["answer"].lower() or "missing" in data["answer"].lower() or "salary" in data["answer"].lower()
