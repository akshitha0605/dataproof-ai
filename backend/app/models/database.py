import sqlite3
import json
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "dataproof.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id TEXT PRIMARY KEY,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        profile_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        dataset_ids TEXT NOT NULL,
        question TEXT NOT NULL,
        status TEXT NOT NULL,
        answer TEXT NOT NULL,
        proof_code TEXT,
        execution_result_json TEXT,
        analysis_response_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# Auto-initialize DB schema on import
init_db()

def save_dataset_record(dataset_id: str, file_name: str, file_path: str, file_type: str, file_size_bytes: int, profile_dict: dict):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO datasets (id, file_name, file_path, file_type, file_size_bytes, profile_json)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_id, file_name, file_path, file_type, file_size_bytes, json.dumps(profile_dict)))
    conn.commit()
    conn.close()

def get_dataset_record(dataset_id: str):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        record = dict(row)
        record["profile"] = json.loads(record["profile_json"])
        return record
    return None

def list_all_datasets():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, file_type, file_size_bytes, profile_json, created_at FROM datasets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        rec = dict(r)
        profile = json.loads(rec["profile_json"])
        results.append({
            "id": rec["id"],
            "file_name": rec["file_name"],
            "file_type": rec["file_type"],
            "file_size_bytes": rec["file_size_bytes"],
            "row_count": profile.get("row_count", 0),
            "column_count": profile.get("column_count", 0),
            "quality_status": profile.get("quality_status", "Good"),
            "created_at": rec["created_at"]
        })
    return results

def save_analysis_record(analysis_id: str, dataset_ids: list, question: str, status: str, answer: str, proof_code: str, execution_result: any, full_response_dict: dict):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO analyses (id, dataset_ids, question, status, answer, proof_code, execution_result_json, analysis_response_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        analysis_id,
        json.dumps(dataset_ids),
        question,
        status,
        answer,
        proof_code,
        json.dumps(execution_result) if execution_result is not None else None,
        json.dumps(full_response_dict)
    ))
    conn.commit()
    conn.close()

def get_analysis_history(limit: int = 20):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT analysis_response_json FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [json.loads(r["analysis_response_json"]) for r in rows]
