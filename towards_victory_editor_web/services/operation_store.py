"""Durable, queryable snapshots of editor and media operations."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path


class OperationStore:
    """Persist OperationLog snapshots with a bounded event and record lifetime."""

    INTERRUPTED_ERROR = (
        "Server restarted before this operation finished; inspect output files before retrying"
    )
    TERMINAL_STATUSES = ("succeeded", "failed", "cancelled")
    DEFAULT_RETENTION_DAYS = 30

    def __init__(self, path: Path | str, *, retention_days: int = DEFAULT_RETENTION_DAYS) -> None:
        if retention_days < 0:
            raise ValueError("retention_days must be non-negative")
        self.path = Path(path)
        self.retention_seconds = retention_days * 24 * 60 * 60
        self._lock = threading.RLock()
        if str(path) == ":memory:":
            self._connection = sqlite3.connect(":memory:", check_same_thread=False, timeout=5)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self.path, check_same_thread=False, timeout=5)
        with self._connection:
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS operations ("
                "id TEXT PRIMARY KEY, created_at REAL NOT NULL, "
                "kind TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)"
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS operations_recent "
                "ON operations(created_at DESC, id DESC)"
            )
        self._recover_interrupted()
        with self._lock, self._connection:
            self._prune_expired()

    def save(self, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        with self._lock, self._connection:
            self._connection.execute(
                "INSERT INTO operations(id, created_at, kind, status, payload) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET status=excluded.status, payload=excluded.payload",
                (payload["id"], payload["created_at"], payload["kind"], payload["status"], encoded),
            )
            self._prune_expired()

    def get(self, operation_id: str) -> dict[str, object]:
        with self._lock, self._connection:
            self._prune_expired()
            row = self._connection.execute(
                "SELECT payload FROM operations WHERE id = ?", (operation_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown operation: {operation_id}")
        return json.loads(row[0])

    def recent(
        self, *, limit: int = 25, kind: str | None = None, status: str | None = None
    ) -> list[dict[str, object]]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        conditions: list[str] = []
        values: list[object] = []
        for column, value in (("kind", kind), ("status", status)):
            if value is not None:
                conditions.append(f"{column} = ?")
                values.append(value)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        with self._lock, self._connection:
            self._prune_expired()
            rows = self._connection.execute(
                "SELECT payload FROM operations" + where + " ORDER BY created_at DESC, id DESC LIMIT ?",
                (*values, limit),
            ).fetchall()
        return [
            {key: value for key, value in json.loads(row[0]).items() if key != "events"}
            for row in rows
        ]

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def _prune_expired(self) -> None:
        cutoff = time.time() - self.retention_seconds
        rows = self._connection.execute(
            "SELECT id, payload FROM operations "
            "WHERE created_at < ? AND status IN (?, ?, ?)",
            (cutoff, *self.TERMINAL_STATUSES),
        ).fetchall()
        expired_ids: list[tuple[str]] = []
        for operation_id, encoded in rows:
            payload = json.loads(encoded)
            finished_at = payload.get("finished_at")
            if isinstance(finished_at, (int, float)) and finished_at < cutoff:
                expired_ids.append((operation_id,))
        if expired_ids:
            self._connection.executemany(
                "DELETE FROM operations WHERE id = ?", expired_ids
            )

    def _recover_interrupted(self) -> None:
        with self._lock:
            rows = self._connection.execute(
                "SELECT payload FROM operations WHERE status NOT IN ('succeeded', 'failed', 'cancelled')"
            ).fetchall()
            for (encoded,) in rows:
                payload = json.loads(encoded)
                now = time.time()
                payload["status"] = "failed"
                payload["error"] = self.INTERRUPTED_ERROR
                payload["finished_at"] = now
                events = payload["events"]
                events.append({"at": now, "level": "error", "message": self.INTERRUPTED_ERROR})
                payload["events"] = events[-500:]
                self.save(payload)
