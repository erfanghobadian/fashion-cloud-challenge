import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from src.transformers import Builder, Mapper

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"


@pytest.fixture
def full_catalog(pricat_path, mappings_path, csv_reader):
    headers, pricat_rows = csv_reader.read(pricat_path)
    _, mapping_rows = csv_reader.read(mappings_path)
    engine = Mapper.from_rows(mapping_rows)
    return Builder(engine).build(headers, pricat_rows)


class TestIntegration:
    def test_catalog_structure(self, full_catalog):
        assert full_catalog.brand == "Via Vai"
        assert len(full_catalog.articles) == 2
        total = sum(len(a.variations) for a in full_catalog.articles)
        assert total == 49

    def test_specific_ean_mapping(self, full_catalog):
        found = None
        for article in full_catalog.articles:
            for v in article.variations:
                if v.get("ean") == "8719245200978":
                    found = v
                    break
        assert found is not None
        assert found["season"] == "Winter"
        assert found["size"] == "European size 38"
        assert found["article_structure"] == "Pump"
        assert found["color"] == "Nero"

    def test_no_consumed_columns_in_output(self, full_catalog):
        forbidden = {"size_group_code", "size_code", "article_structure_code", "color_code"}
        for article in full_catalog.articles:
            for v in article.variations:
                assert not forbidden & set(v.fields)

    def test_no_empty_values(self, full_catalog):
        for article in full_catalog.articles:
            for v in article.variations:
                assert all(v.fields.values())

    def _run_cli(self, *extra_args):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = Path(f.name)
        result = subprocess.run(
            [
                sys.executable, "-m", "src.transform",
                "--pricat", str(_DATA_DIR / "pricat.csv"),
                "--mappings", str(_DATA_DIR / "mappings.csv"),
                "--output", str(output_path),
                *extra_args,
            ],
            capture_output=True, text=True,
            cwd=str(_PROJECT_ROOT),
        )
        return result, output_path

    def test_cli_produces_valid_json(self):
        result, path = self._run_cli()
        try:
            assert result.returncode == 0, result.stderr
            with open(path) as f:
                data = json.load(f)
            assert len(data["catalog"]["articles"]) == 2
        finally:
            path.unlink()

    def test_cli_with_combine_flag(self):
        result, path = self._run_cli("--combine", "price_buy_net,currency")
        try:
            assert result.returncode == 0, result.stderr
            with open(path) as f:
                data = json.load(f)
            assert "price_buy_net_currency" in data["catalog"]["articles"][0]["variations"][0]
        finally:
            path.unlink()

    def test_cli_missing_file_exits_with_error(self):
        result = subprocess.run(
            [
                sys.executable, "-m", "src.transform",
                "--pricat", "/nonexistent.csv",
                "--mappings", "/nonexistent.csv",
                "--output", "/tmp/out.json",
            ],
            capture_output=True, text=True,
            cwd=str(_PROJECT_ROOT),
        )
        assert result.returncode == 1
        assert "Error" in result.stderr
