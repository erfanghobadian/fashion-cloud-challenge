import tempfile
from pathlib import Path

import pytest

from src.exceptions import FileReadError


class TestCsvReaderErrors:
    def test_file_not_found(self, csv_reader):
        with pytest.raises(FileReadError, match="File not found"):
            csv_reader.read("/nonexistent/path.csv")

    def test_empty_file(self, csv_reader):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")
            path = Path(f.name)
        try:
            with pytest.raises(FileReadError, match="No header row"):
                csv_reader.read(str(path))
        finally:
            path.unlink()
