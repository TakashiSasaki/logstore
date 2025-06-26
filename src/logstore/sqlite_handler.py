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
        self.conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table} (\n"
            "  created REAL,\n"
            "  level TEXT,\n"
            "  message TEXT\n"
            ")"
        )
        self.conn.commit()

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.conn.execute(
            f"INSERT INTO {self.table} (created, level, message) VALUES (?, ?, ?)",
            (record.created, record.levelname, msg),
        )
        self.conn.commit()

    def close(self) -> None:
        try:
            self.conn.commit()
        finally:
            super().close()
