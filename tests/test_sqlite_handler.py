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

    cursor = conn.execute('SELECT name, levelno, level, message FROM logs')
    row = cursor.fetchone()

    assert row == (
        'testlogger',
        logging.INFO,
        'INFO',
        'hello world',
    )
