import pytest

from src.transformers import FieldCombiner


class TestCombine:
    @pytest.mark.parametrize("spec, data, expected_key, expected_value", [
        (["price_buy_net", "currency"], {"price_buy_net": "58.5", "currency": "EUR", "ean": "123"}, "price_buy_net_currency", "58.5 EUR"),
        (["a", "b", "c"], {"a": "1", "b": "2", "c": "3", "other": "x"}, "a_b_c", "1 2 3"),
    ])
    def test_combines_and_removes_originals(self, spec, data, expected_key, expected_value):
        result = FieldCombiner([spec]).combine(data)
        assert result[expected_key] == expected_value
        for field in spec:
            assert field not in result

    @pytest.mark.parametrize("spec, data", [
        (["price_buy_net", "currency"], {"price_buy_net": "58.5", "ean": "123"}),
        (["price_buy_net", "nonexistent"], {"price_buy_net": "58.5", "ean": "123"}),
    ])
    def test_skips_when_field_missing(self, spec, data):
        result = FieldCombiner([spec]).combine(data)
        combined_key = "_".join(spec)
        assert combined_key not in result
        assert result["price_buy_net"] == "58.5"
