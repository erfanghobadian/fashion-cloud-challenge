import pytest

from src.exceptions import MappingError
from src.transformers import Mapper


class TestMapper:
    def test_applies_all_mappings(self, sample_mapping_rows, sample_pricat_row):
        engine = Mapper.from_rows(sample_mapping_rows)
        result = engine.apply(sample_pricat_row)
        assert result == {
            "season": "Winter",
            "collection": "Winter Collection 2017/2018",
            "size": "European size 38",
            "article_structure": "Pump",
            "color": "Nero",
        }

    def test_unmapped_value_skipped(self, sample_mapping_rows):
        engine = Mapper.from_rows(sample_mapping_rows)
        row = {"season": "autumn", "collection": "", "size_group_code": "",
               "size_code": "", "article_structure_code": "", "color_code": ""}
        result = engine.apply(row)
        assert "season" not in result

    def test_consumed_columns(self, full_engine):
        assert full_engine.consumed_columns == {
            "season", "collection", "size_group_code", "size_code",
            "article_structure_code", "color_code",
        }

    def test_missing_columns_raises(self):
        with pytest.raises(MappingError, match="missing columns"):
            Mapper.from_rows([{"source": "x", "destination": "X"}])

    def test_composite_partial_key_no_match(self, sample_mapping_rows):
        engine = Mapper.from_rows(sample_mapping_rows)
        row = {"size_group_code": "EU", "size_code": "", "season": "winter",
               "collection": "", "article_structure_code": "", "color_code": ""}
        result = engine.apply(row)
        assert "size" not in result
