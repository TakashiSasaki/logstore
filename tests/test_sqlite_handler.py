import logging
import sqlite3

from logstore.sqlite_handler import SQLiteHandler


def test_logging_inserts_records():
    conn = sqlite3.connect(':memory:')
    handler = SQLiteHandler(conn)
    logger = logging.getLogger('testlogger')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info('hello world')

    cursor = conn.execute('SELECT level, message FROM logs')
    rows = cursor.fetchall()
    assert rows == [('INFO', 'hello world')]
