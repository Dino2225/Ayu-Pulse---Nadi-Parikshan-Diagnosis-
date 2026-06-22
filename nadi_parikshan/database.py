import os
import sqlite3
from pathlib import Path

# Database path: prefer environment override, then private_artifacts/patients.db if present
DEFAULT_DB = 'patients.db'
env_db = os.environ.get('NADI_DB')
pkg_root = Path(__file__).resolve().parent.parent
private_db = pkg_root / 'private_artifacts' / 'patients.db'
DATABASE = env_db if env_db else (str(private_db) if private_db.exists() else DEFAULT_DB)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            prediction TEXT,
            accuracy REAL,
            bpm1 REAL,
            bpm2 REAL,
            bpm3 REAL,
            vata_balance REAL,
            pitta_balance REAL,
            kapha_balance REAL,
            dominant_dosha TEXT,
            statistics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        conn.execute('ALTER TABLE patients ADD COLUMN vata_balance REAL')
        conn.execute('ALTER TABLE patients ADD COLUMN pitta_balance REAL')
        conn.execute('ALTER TABLE patients ADD COLUMN kapha_balance REAL')
        conn.execute('ALTER TABLE patients ADD COLUMN dominant_dosha TEXT')
        conn.execute('ALTER TABLE patients ADD COLUMN statistics TEXT')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()
