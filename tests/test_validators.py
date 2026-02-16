from decimal import Decimal

import pytest

from src.exceptions import ValidationError
from src.models.validators import validate_currency, validate_ean, validate_not_empty, validate_price


class TestValidators:
    @pytest.mark.parametrize("ean, error", [
        ("8719245200978", None),
        ("96385074", None),
        ("ABC1234567890", "numeric"),
        ("123456", "digits"),
    ])
    def test_ean(self, ean, error):
        if error is None:
            assert validate_ean(ean) == ean
        else:
            with pytest.raises(ValidationError, match=error):
                validate_ean(ean)

    @pytest.mark.parametrize("value, error", [
        (Decimal("58.5"), None),
        (None, None),
        (Decimal("-10"), "negative"),
    ])
    def test_price(self, value, error):
        if error is None:
            assert validate_price(value, "price") == value
        else:
            with pytest.raises(ValidationError, match=error):
                validate_price(value, "price")

    @pytest.mark.parametrize("value, error", [
        ("EUR", None),
        ("USD", None),
        ("", None),
        ("eur", "ISO"),
        ("EU", "ISO"),
        ("1234", "ISO"),
    ])
    def test_currency(self, value, error):
        if error is None:
            assert validate_currency(value) == value
        else:
            with pytest.raises(ValidationError, match=error):
                validate_currency(value)

    @pytest.mark.parametrize("value, error", [
        ("15189-02", None),
        ("", "empty"),
        ("   ", "empty"),
    ])
    def test_not_empty(self, value, error):
        if error is None:
            assert validate_not_empty(value, "field") == value
        else:
            with pytest.raises(ValidationError, match=error):
                validate_not_empty(value, "field")
