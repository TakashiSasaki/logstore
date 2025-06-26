import os
import sys
import importlib
import httpimport

GITHUB_USER = "TakashiSasaki"
GITHUB_REPO = "logstore"
GITHUB_REF = "refs/heads/main/src"

def test_httpimport_remote():
    local_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
    if local_src in sys.path:
        sys.path.remove(local_src)
        removed = True
    else:
        removed = False
    try:
        with httpimport.github_repo(GITHUB_USER, GITHUB_REPO, ref=GITHUB_REF):
            mod = importlib.import_module('logstore')
            assert hasattr(mod, 'SQLiteHandler')
    finally:
        if removed:
            sys.path.insert(0, local_src)

