from decimal import Decimal
from typing import ClassVar

from ..exceptions import ValidationError


class ValidatedMixin:
    _validators: ClassVar[dict] = {}

    def __setattr__(self, name, value):
        if validator := self._validators.get(name):
            value = validator(value)
        super().__setattr__(name, value)


def validate_ean(value: str) -> str:
    if not value or not value.isdigit():
        raise ValidationError(f"EAN must be numeric, got: {value!r}")
    if len(value) not in (8, 12, 13, 14):
        raise ValidationError(f"EAN must be 8, 12, 13 or 14 digits, got {len(value)}")
    # TODO: add check digit validationas well
    return value


def validate_price(value: Decimal | None, field_name: str) -> Decimal | None:
    if value is None:
        return None
    if value < 0:
        raise ValidationError(f"{field_name} cannot be negative: {value}")
    return value



def validate_currency(value: str) -> str:
    if not value:
        return value
    if len(value) != 3 or not value.isalpha() or not value.isupper():
        raise ValidationError(f"Currency must be 3-letter ISO code, got: {value!r}")
    return value


def validate_not_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty")
    return value
