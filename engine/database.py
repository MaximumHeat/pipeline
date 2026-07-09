import sqlite3
import uuid
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pipeline.db")


def get_connection(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            target_url TEXT NOT NULL,
            current_iteration INTEGER DEFAULT 0,
            pipeline_status TEXT CHECK(pipeline_status IN ('RUNNING', 'REJECTED', 'COMPLETED', 'FAILED')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS iteration_telemetry (
            telemetry_id TEXT PRIMARY KEY,
            run_id TEXT,
            iteration_index INTEGER NOT NULL,
            scuba_raw_output_path TEXT,
            mozart_synthesis_path TEXT,
            pnut_score REAL,
            pnut_critique_summary TEXT,
            FOREIGN KEY(run_id) REFERENCES pipeline_runs(run_id)
        )
    """)
    conn.commit()
    return conn


def create_run(target_url: str, db_path: str = DB_PATH) -> str:
    run_id = str(uuid.uuid4())
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO pipeline_runs (run_id, target_url, pipeline_status) VALUES (?, ?, 'RUNNING')",
        (run_id, target_url)
    )
    conn.commit()
    conn.close()
    return run_id


def update_run_status(run_id: str, status: str, iteration: int = None, db_path: str = DB_PATH):
    conn = get_connection(db_path)
    if iteration is not None:
        conn.execute(
            "UPDATE pipeline_runs SET pipeline_status = ?, current_iteration = ? WHERE run_id = ?",
            (status, iteration, run_id)
        )
    else:
        conn.execute(
            "UPDATE pipeline_runs SET pipeline_status = ? WHERE run_id = ?",
            (status, run_id)
        )
    conn.commit()
    conn.close()


def insert_iteration(run_id: str, iteration_index: int, scuba_raw_output_path: str = None,
                     mozart_synthesis_path: str = None, pnut_score: float = None,
                     pnut_critique_summary: str = None, db_path: str = DB_PATH):
    telemetry_id = str(uuid.uuid4())
    conn = get_connection(db_path)
    conn.execute(
        """INSERT INTO iteration_telemetry
           (telemetry_id, run_id, iteration_index, scuba_raw_output_path,
            mozart_synthesis_path, pnut_score, pnut_critique_summary)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (telemetry_id, run_id, iteration_index, scuba_raw_output_path,
         mozart_synthesis_path, pnut_score, pnut_critique_summary)
    )
    conn.commit()
    conn.close()
