import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "netscope.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS scans (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            target      TEXT NOT NULL,
            hostname    TEXT,
            start_time  TEXT,
            end_time    TEXT,
            duration    REAL,
            total_ports INTEGER,
            open_count  INTEGER,
            critical    INTEGER DEFAULT 0,
            high        INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id     INTEGER NOT NULL,
            port        INTEGER NOT NULL,
            state       TEXT,
            service     TEXT,
            banner      TEXT,
            cve         TEXT,
            severity    TEXT DEFAULT 'NONE',
            cve_desc    TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
        );
        """)

def save_scan(scan_result) -> int:
    critical = sum(1 for p in scan_result.open_ports if p.severity == "CRITICAL")
    high     = sum(1 for p in scan_result.open_ports if p.severity == "HIGH")
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO scans (target, hostname, start_time, end_time, duration, total_ports, open_count, critical, high)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_result.target,
            scan_result.hostname,
            scan_result.start_time,
            scan_result.end_time,
            scan_result.duration,
            scan_result.total_scanned,
            len(scan_result.open_ports),
            critical,
            high
        ))
        scan_id = cur.lastrowid
        conn.executemany("""
            INSERT INTO ports (scan_id, port, state, service, banner, cve, severity, cve_desc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (scan_id, p.port, p.state, p.service, p.banner, p.cve, p.severity, p.cve_desc)
            for p in scan_result.open_ports
        ])
    return scan_id

def get_scans(limit: int = 20):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM scans ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_scan_detail(scan_id: int):
    with get_conn() as conn:
        scan = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        if not scan:
            return None
        ports = conn.execute(
            "SELECT * FROM ports WHERE scan_id = ? ORDER BY port", (scan_id,)
        ).fetchall()
    return {
        "scan": dict(scan),
        "ports": [dict(p) for p in ports]
    }

def delete_scan(scan_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))