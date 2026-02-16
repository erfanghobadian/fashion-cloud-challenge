from dataclasses import dataclass, field
from decimal import Decimal
from functools import partial
from typing import ClassVar

from .validators import (
    ValidatedMixin,
    validate_currency,
    validate_ean,
    validate_not_empty,
    validate_price,
)


@dataclass
class Variation(ValidatedMixin):
    ean: str
    price_buy_net: Decimal | None = None
    price_sell: Decimal | None = None
    currency: str = ""
    extras: dict[str, str] = field(default_factory=dict)

    _validators: ClassVar[dict] = {
        "ean": validate_ean,
        "price_buy_net": partial(validate_price, field_name="price_buy_net"),
        "price_sell": partial(validate_price, field_name="price_sell"),
        "currency": validate_currency,
    }

    @property
    def fields(self) -> dict:
        result: dict = {"ean": self.ean}
        if self.price_buy_net is not None:
            result["price_buy_net"] = float(self.price_buy_net)
        if self.price_sell is not None:
            result["price_sell"] = float(self.price_sell)
        if self.currency:
            result["currency"] = self.currency
        result.update(self.extras)
        return result

    def __getitem__(self, key: str) -> str:
        return self.fields[key]

    def __contains__(self, key: str) -> bool:
        return key in self.fields

    def get(self, key: str, default: str = "") -> str:
        return self.fields.get(key, default)


@dataclass
class Article(ValidatedMixin):
    article_number: str
    variations: list[Variation] = field(default_factory=list)

    _validators: ClassVar[dict] = {
        "article_number": partial(validate_not_empty, field_name="article_number"),
    }


@dataclass
class Catalog(ValidatedMixin):
    brand: str
    articles: list[Article] = field(default_factory=list)

    _validators: ClassVar[dict] = {
        "brand": partial(validate_not_empty, field_name="brand"),
    }
