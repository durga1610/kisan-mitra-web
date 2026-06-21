"""
db_utils.py
-----------
Shared SQLite utilities for Kisan Mitra backend.

Key features:
  - WAL mode + busy_timeout on every new connection  (eliminates "database is locked")
  - Async write queue for all non-critical analytics writes
    (gemini_fallback_log, gemini_daily_usage, gemini_response_cache,
     gemini_optimization_stats, dataset_v2_entries)
  - get_db_connection() — one-liner that returns a WAL-mode connection
  - fire_and_forget_write() — submit any SQL write without blocking the request thread
"""

import sqlite3
import threading
import logging
import queue
import time
from typing import Optional, Tuple, List, Any

from config import DB_PATH

logger = logging.getLogger(__name__)

# ── WAL + busy_timeout ────────────────────────────────────────────────────────
_BUSY_TIMEOUT_MS = 5000   # 5 s — wait this long before raising OperationalError


def get_db_connection(path: str = DB_PATH) -> sqlite3.Connection:
    """
    Return a SQLite connection with WAL journal mode and a 5-second busy
    timeout.  Both settings are applied atomically after connect so that
    concurrent readers/writers never see "database is locked".

    WAL mode allows one writer + many concurrent readers.
    busy_timeout makes SQLite retry internally instead of raising immediately.
    """
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode (idempotent — safe to call on every connection)
    conn.execute("PRAGMA journal_mode=WAL")
    # Busy handler: retry for up to 5 seconds before raising
    conn.execute(f"PRAGMA busy_timeout={_BUSY_TIMEOUT_MS}")
    # Recommended pragmas for durability + speed
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-8000")   # 8 MB page cache
    return conn


# ── Background write queue ────────────────────────────────────────────────────
# Non-critical analytics writes (log rows, cache entries, counters) are
# dispatched to a single background worker thread so they never block the
# request/response cycle.
#
# Format of each queue item: (sql: str, params: tuple)
#   OR a callable with no arguments for complex operations.

_write_queue: queue.Queue = queue.Queue(maxsize=2000)
_worker_started = False
_worker_lock = threading.Lock()


def _write_worker():
    """
    Single background thread that drains the async write queue.
    Uses one persistent WAL connection to batch consecutive writes efficiently.
    """
    logger.info("[DB Utils] Background write worker started.")
    conn: Optional[sqlite3.Connection] = None

    while True:
        try:
            item = _write_queue.get(timeout=5)   # block up to 5 s

            if item is None:                       # poison-pill shutdown signal
                break

            if conn is None or _is_closed(conn):
                conn = get_db_connection()

            try:
                if callable(item):
                    item()                         # complex operation
                else:
                    sql, params = item
                    conn.execute(sql, params)
                    conn.commit()
            except Exception as exc:
                logger.warning("[DB Utils] Async write failed: %s", exc)
                # Re-open connection on next iteration
                try:
                    conn.close()
                except Exception:
                    pass
                conn = None

            _write_queue.task_done()

        except queue.Empty:
            # Flush any pending transaction
            if conn and not _is_closed(conn):
                try:
                    conn.commit()
                except Exception:
                    pass
        except Exception as exc:
            logger.error("[DB Utils] Write worker error: %s", exc)


def _is_closed(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("SELECT 1")
        return False
    except Exception:
        return True


def _ensure_worker():
    global _worker_started
    if not _worker_started:
        with _worker_lock:
            if not _worker_started:
                t = threading.Thread(target=_write_worker, daemon=True, name="db-write-worker")
                t.start()
                _worker_started = True


def fire_and_forget_write(sql: str, params: tuple = ()):
    """
    Submit a SQL write to the background worker.  Returns immediately.
    Drops the write (with a warning) if the queue is full.
    """
    _ensure_worker()
    try:
        _write_queue.put_nowait((sql, params))
    except queue.Full:
        logger.warning("[DB Utils] Async write queue full — dropping write: %.80s", sql)


def fire_and_forget_callable(fn):
    """
    Submit an arbitrary callable to the background worker.  Returns immediately.
    Use when a write operation is too complex for a single SQL statement.
    """
    _ensure_worker()
    try:
        _write_queue.put_nowait(fn)
    except queue.Full:
        logger.warning("[DB Utils] Async write queue full — dropping callable: %s", fn)
