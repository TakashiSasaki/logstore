"""SQLite logging handler for Python logging.

Example
-------
    import logging
    import sqlite3
    from logstore.sqlite_handler import SQLiteHandler

    conn = sqlite3.connect(':memory:')
    handler = SQLiteHandler(conn)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.warning('hi')
"""
import json
import logging
import sqlite3
from typing import Any, Dict, Optional

class SQLiteHandler(logging.Handler):
    """Logging handler that writes records to a SQLite database.

    Parameters
    ----------
    conn : sqlite3.Connection
        Connection object used to write log records. You may use a connection
        from :func:`sqlite3.connect`, e.g.::

            conn = sqlite3.connect(':memory:')
            handler = SQLiteHandler(conn)
            logger = logging.getLogger('myapp')
            logger.addHandler(handler)

    table : str, optional
        Name of the table to insert log records into. The table will be
        created if it does not already exist.
    """

    def __init__(self, conn: sqlite3.Connection, table: str = "logs") -> None:
        super().__init__()
        self.conn = conn
        self.table = table
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create the log table if it does not already exist."""

        self.conn.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table} (
                timestamp REAL NOT NULL,
                severity INTEGER NOT NULL,
                message TEXT NOT NULL,
                source TEXT NOT NULL,
                process_id INTEGER NOT NULL,
                details_json TEXT
            )"""
        )
        self.conn.commit()

    def _extract_details(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Return a dictionary of LogRecord attributes not stored in core columns."""

        excluded = {
            "created",
            "levelno",
            "msg",
            "args",
            "name",
            "process",
            "message",
        }
        details = {}
        for key, value in record.__dict__.items():
            if key in excluded:
                continue
            try:
                json.dumps(value)
                details[key] = value
            except TypeError:
                details[key] = str(value)
        return details

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        details = self._extract_details(record)
        self.conn.execute(
            f"INSERT INTO {self.table} (timestamp, severity, message, source, process_id, details_json) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                record.created,
                record.levelno,
                msg,
                record.name,
                getattr(record, "process", None),
                json.dumps(details),
            ),
        )
        self.conn.commit()

    def close(self) -> None:
        try:
            self.conn.commit()
        finally:
            super().close()
