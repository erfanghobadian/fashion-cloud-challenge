import os
import tempfile

from src.models import Article, Catalog, Variation
from src.repositories import JsonCatalogRepository


class TestJsonCatalogRepository:
    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            catalog = Catalog(
                brand="Via Vai",
                articles=[Article("15189-02", [
                    Variation(ean="8719245200978", extras={"color": "Nero"}),
                ])],
            )
            repo = JsonCatalogRepository(path)
            repo.save(catalog)

            loaded = repo.load()
            assert loaded["catalog"]["brand"] == "Via Vai"
            assert loaded["catalog"]["articles"][0]["article_number"] == "15189-02"
            assert loaded["catalog"]["articles"][0]["variations"][0]["ean"] == "8719245200978"
        finally:
            if os.path.exists(path):
                os.unlink(path)
