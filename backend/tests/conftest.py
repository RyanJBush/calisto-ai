import os
import tempfile

_TEST_DB_FILE = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TEST_DB_FILE.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_FILE.name}"
