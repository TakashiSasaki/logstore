import logging
import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logstore.sqlite_handler import SQLiteHandler


def test_logging_inserts_records(monkeypatch):
    conn = sqlite3.connect(':memory:')
    handler = SQLiteHandler(conn)
    logger = logging.getLogger('testlogger')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    fixed_time = 1700000000.0
    monkeypatch.setattr(logging.time, "time", lambda: fixed_time)

    logger.info("hello world")

    cursor = conn.execute(
        "SELECT created, name, levelno, level, message FROM logs"
    )
    row = cursor.fetchone()

    expected_filetime = int((fixed_time + 11644473600) * 10_000_000)

    assert row == (
        expected_filetime,
        "testlogger",
        logging.INFO,
        "INFO",
        "hello world",
    )
