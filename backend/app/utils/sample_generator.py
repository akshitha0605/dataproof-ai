import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent.parent.parent / "sample_data"

def ensure_sample_datasets():
    """
    Generates synthetic sample files in backend/sample_data/ if they do not exist.
    These are ordinary data files processed through the 100% generic dynamic pipeline.
    """
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Sales Transactions (CSV)
    csv_path = SAMPLE_DIR / "sales_transactions.csv"
    if not csv_path.exists():
        np.random.seed(42)
        dates = pd.date_range("2025-01-01", periods=100, freq="D")
        regions = ["North", "South", "East", "West", "Central"]
        categories = ["Electronics", "Furniture", "Office Supplies", "Apparel"]
        df_sales = pd.DataFrame({
            "Transaction_ID": [f"TXN-{1000+i}" for i in range(100)],
            "Date": dates,
            "Region": np.random.choice(regions, 100),
            "Category": np.random.choice(categories, 100),
            "Units_Sold": np.random.randint(1, 50, 100),
            "Unit_Price": np.random.choice([19.99, 49.99, 129.99, 299.99, 899.99], 100),
            "Customer_Rating": np.round(np.random.uniform(3.0, 5.0, 100), 1)
        })
        df_sales["Total_Amount"] = df_sales["Units_Sold"] * df_sales["Unit_Price"]
        df_sales.to_csv(csv_path, index=False)

    # 2. Student Records (Excel multi-sheet)
    xlsx_path = SAMPLE_DIR / "student_performance.xlsx"
    if not xlsx_path.exists():
        df_students = pd.DataFrame({
            "Student_ID": [f"STU-{200+i}" for i in range(50)],
            "Student_Name": [f"Student_{i+1}" for i in range(50)],
            "Department": np.random.choice(["Computer Science", "Data Science", "Electrical", "Mechanical"], 50),
            "Enrollment_Year": np.random.choice([2022, 2023, 2024], 50),
            "Attendance_Percentage": np.random.randint(65, 100, 50)
        })
        df_grades = pd.DataFrame({
            "Student_ID": [f"STU-{200+i}" for i in range(50)],
            "Midterm_Score": np.random.randint(40, 100, 50),
            "Final_Score": np.random.randint(45, 100, 50),
            "CGPA": np.round(np.random.uniform(2.5, 4.0, 50), 2)
        })
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            df_students.to_excel(writer, sheet_name="Students", index=False)
            df_grades.to_excel(writer, sheet_name="Grades", index=False)

    # 3. IoT Sensor Telemetry (JSON)
    json_path = SAMPLE_DIR / "iot_telemetry.json"
    if not json_path.exists():
        iot_records = []
        devices = ["Sensor-A1", "Sensor-B2", "Sensor-C3", "Sensor-D4"]
        locations = ["Zone-1", "Zone-2", "Zone-3"]
        for i in range(80):
            iot_records.append({
                "reading_id": f"READ-{5000+i}",
                "timestamp": f"2026-03-01T{i%24:02d}:15:00Z",
                "device_id": devices[i % len(devices)],
                "location": locations[i % len(locations)],
                "temperature_celsius": round(20.0 + (i % 15) * 0.8 + np.random.normal(0, 0.5), 2),
                "humidity_pct": round(40.0 + (i % 20) * 1.1, 1),
                "battery_level_pct": max(10, 100 - i)
            })
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(iot_records, f, indent=2)

    # 4. Hospital Expenditure (TSV)
    tsv_path = SAMPLE_DIR / "hospital_expenditure.tsv"
    if not tsv_path.exists():
        df_hosp = pd.DataFrame({
            "Expense_ID": [f"EXP-{300+i}" for i in range(60)],
            "Department": np.random.choice(["Cardiology", "Neurology", "Pediatrics", "Oncology", "Radiology"], 60),
            "Expense_Category": np.random.choice(["Equipment", "Supplies", "Maintenance", "Staffing", "Software"], 60),
            "Cost_USD": np.random.randint(500, 25000, 60),
            "Approval_Status": np.random.choice(["Approved", "Pending", "Rejected"], 60, p=[0.8, 0.15, 0.05])
        })
        df_hosp.to_csv(tsv_path, sep="\t", index=False)
