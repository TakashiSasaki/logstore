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
                created REAL,
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
                record.created,
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
