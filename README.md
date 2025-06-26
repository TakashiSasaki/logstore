# logstore

Utilities for logging to SQLite databases.

This package provides a simple logging handler that writes log records to a
SQLite database.  It captures a rich set of attributes from each
``LogRecord`` so that log entries include not only the formatted message but
also contextual information such as the logger name, file, line number and
process/thread identifiers.

## Importing with `httpimport`

You can use [`httpimport`](https://pypi.org/project/httpimport/) to load
``logstore`` directly from GitHub without installing it.  This can be useful
in notebooks or throwaway scripts:

```python
import httpimport

with httpimport.github_repo('TakashiSasaki', 'logstore', ref='refs/heads/main/src'):
    from logstore import SQLiteHandler

```

After the ``with`` block exits the module is removed from ``sys.modules``.
