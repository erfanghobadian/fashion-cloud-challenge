import logging
from decimal import Decimal, InvalidOperation

from ..exceptions import CatalogBuildError
from ..models import Article, Catalog, Variation
from .combiner import FieldCombiner
from .mapper import Mapper


logger = logging.getLogger(__name__)


class Builder:

    CATALOG_LEVEL_FIELDS = frozenset({"brand"})
    ARTICLE_KEY_FIELD = "article_number"

    def __init__(
        self,
        engine: Mapper,
        combiner: FieldCombiner | None = None,
    ) -> None:
        self._engine = engine
        self._combiner = combiner

    def build(self, headers: list[str], rows: list[dict[str, str]]) -> Catalog:
        if not rows:
            raise CatalogBuildError("No pricat rows to process")

        first_row = rows[0]
        if self.ARTICLE_KEY_FIELD not in first_row:
            raise CatalogBuildError(
                f"Required field '{self.ARTICLE_KEY_FIELD}' not found in pricat data"
            )

        brand = first_row.get("brand", "")
        mixed = {row.get("brand", "") for row in rows} - {brand}
        if mixed:
            raise CatalogBuildError(
                f"Expected a single brand but found multiple: {{{brand!r}, {', '.join(repr(b) for b in sorted(mixed))}}}"
            )

        articles: dict[str, Article] = {}

        for row in rows:
            article_num = row[self.ARTICLE_KEY_FIELD]
            if article_num not in articles:
                articles[article_num] = Article(article_number=article_num)
            articles[article_num].variations.append(self._transform_row(row, headers))

        total_variations = sum(len(a.variations) for a in articles.values())
        logger.info("Built catalog: brand=%r, %d articles, %d variations",
                    brand, len(articles), total_variations)

        return Catalog(
            brand=brand,
            articles=list(articles.values()),
        )

    def _transform_row(self, row: dict[str, str], headers: list[str]) -> Variation:
        flat = self._engine.apply(row)

        skip = (
            self._engine.consumed_columns
            | self.CATALOG_LEVEL_FIELDS
            | {self.ARTICLE_KEY_FIELD}
        )
        for col in headers:
            if col not in skip and row.get(col, ""):
                flat[col] = row[col]

        if self._combiner:
            flat = self._combiner.combine(flat)

        return Variation(
            ean=flat.pop("ean", ""),
            price_buy_net=self._to_decimal(flat.pop("price_buy_net", ""), "price_buy_net"),
            price_sell=self._to_decimal(flat.pop("price_sell", ""), "price_sell"),
            currency=flat.pop("currency", ""),
            extras=flat,
        )

    @staticmethod
    def _to_decimal(value: str, field_name: str = "") -> Decimal | None:
        if not value:
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            logger.warning("Could not parse %r as decimal for %s", value, field_name)
            return None
