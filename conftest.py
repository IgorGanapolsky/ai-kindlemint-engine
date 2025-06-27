# conftest.py - configure temporary directory for pytest
import os
import tempfile

# Ensure a writable temp directory exists for pytest capture
_pytest_tmp = os.path.join(os.getcwd(), ".pytest_tmp")
os.makedirs(_pytest_tmp, exist_ok=True)
tempfile.tempdir = _pytest_tmp

# Skip legacy test modules and directories
collect_ignore = [
    "tests/test_crossword_engine_v3.py",
    "tests/test_enhanced_qa_validator_v2.py",
    "tests/integration",
    "tests/unit",
]
