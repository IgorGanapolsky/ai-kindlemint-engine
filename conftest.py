# conftest.py - configure temporary directory for pytest
import os
import tempfile

# Ensure a writable temp directory exists for pytest capture
_pytest_tmp = os.path.join(os.getcwd(), '.pytest_tmp')
os.makedirs(_pytest_tmp, exist_ok=True)
tempfile.tempdir = _pytest_tmp
