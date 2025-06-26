import json
import logging
import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logstore.sqlite_handler import SQLiteHandler


def test_logging_inserts_records():
    conn = sqlite3.connect(':memory:')
    handler = SQLiteHandler(conn)
    logger = logging.getLogger('testlogger')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info('hello world')

    cursor = conn.execute(
        'SELECT source, severity, message, process_id, details_json FROM logs'
    )
    row = cursor.fetchone()

    assert row[0] == 'testlogger'
    assert row[1] == logging.INFO
    assert row[2] == 'hello world'
    assert row[3] == os.getpid()
    details = json.loads(row[4])
    assert 'pathname' in details
