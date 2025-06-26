# logstore

Utilities for logging to SQLite databases.

This package provides a simple logging handler that writes log records to a
SQLite database.  It captures a rich set of attributes from each
``LogRecord`` so that log entries include not only the formatted message but
also contextual information such as the logger name, file, line number and
process/thread identifiers.
