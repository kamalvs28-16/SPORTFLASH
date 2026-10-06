import os
import sqlite3
import json
from typing import Dict, Any, List, Optional
from pipeline.config import RESULTS_DIR, BASE_DIR

DB_PATH = os.path.join(RESULTS_DIR, "sportflash.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes SQLite database schema for Matches, Players, Jobs, and Results tables.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        video_path TEXT NOT NULL,
        total_frames INTEGER DEFAULT 0,
        fps REAL DEFAULT 30.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id TEXT NOT NULL,
        match_id TEXT NOT NULL,
        name TEXT NOT NULL,
        jersey_number TEXT,
        team TEXT NOT NULL,
        position TEXT DEFAULT 'Midfielder',
        photo_url TEXT,
        PRIMARY KEY (match_id, player_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        match_id TEXT NOT NULL,
        status TEXT DEFAULT 'idle',
        progress INTEGER DEFAULT 0,
        step_name TEXT DEFAULT 'Idle',
        details TEXT DEFAULT '',
        current_frame INTEGER DEFAULT 0,
        total_frames INTEGER DEFAULT 0,
        error TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id TEXT NOT NULL,
        player_id TEXT,
        category TEXT NOT NULL,
        data_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("[INFO] SQLite database schema initialized clean.")


if __name__ == "__main__":
    init_db()
