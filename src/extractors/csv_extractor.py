import csv
import logging

from ..exceptions import FileReadError

logger = logging.getLogger(__name__)


class CsvReader:

    def __init__(self, delimiter: str = ";") -> None:
        self._delimiter = delimiter

    def read(self, file_path: str) -> tuple[list[str], list[dict[str, str]]]:
        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=self._delimiter)

                if reader.fieldnames is None:
                    raise FileReadError(f"No header row found in {file_path}")

                headers = list(reader.fieldnames)
                rows: list[dict[str, str]] = []
                skipped = 0

                for row in reader:
                    stripped = {k: v.strip() for k, v in row.items()}
                    if any(stripped.values()):
                        rows.append(stripped)
                    else:
                        skipped += 1

                if skipped:
                    logger.info("Skipped %d blank rows in %s", skipped, file_path)

                logger.info("Read %d rows with %d columns from %s", len(rows), len(headers), file_path)
                return headers, rows

        except FileNotFoundError:
            raise FileReadError(f"File not found: {file_path}")
        except UnicodeDecodeError as e:
            raise FileReadError(f"Cannot decode {file_path}: {e}")
