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
import logging
import sqlite3
from typing import Optional

# Seconds between the Windows FILETIME epoch (1601-01-01) and Unix epoch
# (1970-01-01). Used to convert ``LogRecord.created`` values to FILETIME
# timestamps.
_FILETIME_EPOCH_DELTA = 11644473600
_HUNDREDS_OF_NANOSECONDS = 10_000_000


def _to_filetime(timestamp: float) -> int:
    """Convert a POSIX timestamp to Windows FILETIME units."""
    return int((timestamp + _FILETIME_EPOCH_DELTA) * _HUNDREDS_OF_NANOSECONDS)

class SQLiteHandler(logging.Handler):
    """Logging handler that writes records to a SQLite database.

    Each entry stores a 64-bit ``FILETIME`` timestamp representing the log
    time in 100‑nanosecond intervals since 1601‑01‑01.

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
                created INTEGER,
                name TEXT,
                levelno INTEGER,
                level TEXT,
                message TEXT,
                pathname TEXT,
                filename TEXT,
                module TEXT,
                lineno INTEGER,
                funcName TEXT,
                process INTEGER,
                processName TEXT,
                thread INTEGER,
                threadName TEXT
            )"""
        )
        self.conn.commit()

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.conn.execute(
            f"INSERT INTO {self.table} (created, name, levelno, level, message, pathname, filename, module, lineno, funcName, process, processName, thread, threadName) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                _to_filetime(record.created),
                record.name,
                record.levelno,
                record.levelname,
                msg,
                getattr(record, "pathname", None),
                getattr(record, "filename", None),
                getattr(record, "module", None),
                getattr(record, "lineno", None),
                getattr(record, "funcName", None),
                getattr(record, "process", None),
                getattr(record, "processName", None),
                getattr(record, "thread", None),
                getattr(record, "threadName", None),
            ),
        )
        self.conn.commit()

    def close(self) -> None:
        try:
            self.conn.commit()
        finally:
            super().close()
