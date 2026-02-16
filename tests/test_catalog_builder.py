import pytest

from src.exceptions import CatalogBuildError
from src.transformers import Builder, Mapper
from tests.conftest import PRICAT_HEADERS


@pytest.fixture
def builder(sample_mapping_rows):
    return Builder(Mapper.from_rows(sample_mapping_rows))


class TestBuilder:
    def test_mapped_and_passthrough_fields(self, builder, sample_pricat_row):
        catalog = builder.build(PRICAT_HEADERS, [sample_pricat_row])
        v = catalog.articles[0].variations[0]
        assert v["season"] == "Winter"
        assert v["size"] == "European size 38"
        assert v["color"] == "Nero"
        assert v["ean"] == "8719245200978"
        assert v["currency"] == "EUR"
        assert "catalog_code" not in v
        assert "size_group_code" not in v
        assert "brand" not in v
        assert "article_number" not in v

    def test_empty_rows(self, builder):
        with pytest.raises(CatalogBuildError, match="No pricat rows"):
            builder.build(PRICAT_HEADERS, [])

    def test_missing_article_number(self, builder):
        with pytest.raises(CatalogBuildError, match="article_number"):
            builder.build(["brand", "ean"], [{"brand": "Test", "ean": "123"}])

    def test_multiple_brands_raises(self, builder):
        rows = [
            {"brand": "Via Vai", "article_number": "A1", "ean": "8719245200978"},
            {"brand": "Other Brand", "article_number": "A2", "ean": "8719245200985"},
        ]
        with pytest.raises(CatalogBuildError, match="multiple"):
            builder.build(["brand", "article_number", "ean"], rows)
