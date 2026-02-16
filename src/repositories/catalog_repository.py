import json
import logging
from abc import ABC, abstractmethod

from ..models import Catalog

logger = logging.getLogger(__name__)


class CatalogRepository(ABC):

    @abstractmethod
    def save(self, catalog: Catalog) -> None:
        pass

    @abstractmethod
    def load(self) -> dict:
        pass


class JsonCatalogRepository(CatalogRepository):

    def __init__(self, file_path: str, indent: int = 2) -> None:
        self._file_path = file_path
        self._indent = indent

    def save(self, catalog: Catalog) -> None:
        data = {
            "catalog": {
                "brand": catalog.brand,
                "articles": [
                    {
                        "article_number": a.article_number,
                        "variations": [v.fields for v in a.variations],
                    }
                    for a in catalog.articles
                ],
            }
        }
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=self._indent, ensure_ascii=False)
        logger.info("Saved catalog JSON to %s", self._file_path)

    def load(self) -> dict:
        with open(self._file_path, encoding="utf-8") as f:
            return json.load(f)
