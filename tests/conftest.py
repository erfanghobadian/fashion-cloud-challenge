from pathlib import Path

import pytest

from src.extractors import CsvReader
from src.transformers import Mapper

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def csv_reader():
    return CsvReader()


@pytest.fixture
def pricat_path():
    return str(DATA_DIR / "pricat.csv")


@pytest.fixture
def mappings_path():
    return str(DATA_DIR / "mappings.csv")


@pytest.fixture
def sample_pricat_row():
    return {
        "ean": "8719245200978",
        "supplier": "Rupesco BV",
        "brand": "Via Vai",
        "catalog_code": "",
        "collection": "NW 17-18",
        "season": "winter",
        "article_structure_code": "10",
        "article_number": "15189-02",
        "article_number_2": "15189-02 Aviation Nero",
        "article_number_3": "Aviation",
        "color_code": "1",
        "size_group_code": "EU",
        "size_code": "38",
        "size_name": "38",
        "currency": "EUR",
        "price_buy_gross": "",
        "price_buy_net": "58.5",
        "discount_rate": "",
        "price_sell": "139.95",
        "material": "Aviation",
        "target_area": "Woman Shoes",
    }


@pytest.fixture
def sample_mapping_rows():
    return [
        {"source": "winter", "destination": "Winter", "source_type": "season", "destination_type": "season"},
        {"source": "summer", "destination": "Summer", "source_type": "season", "destination_type": "season"},
        {"source": "NW 17-18", "destination": "Winter Collection 2017/2018", "source_type": "collection", "destination_type": "collection"},
        {"source": "EU|38", "destination": "European size 38", "source_type": "size_group_code|size_code", "destination_type": "size"},
        {"source": "10", "destination": "Pump", "source_type": "article_structure_code", "destination_type": "article_structure"},
        {"source": "1", "destination": "Nero", "source_type": "color_code", "destination_type": "color"},
    ]


@pytest.fixture
def full_engine(mappings_path, csv_reader):
    _, rows = csv_reader.read(mappings_path)
    return Mapper.from_rows(rows)


PRICAT_HEADERS = [
    "ean", "supplier", "brand", "catalog_code", "collection", "season",
    "article_structure_code", "article_number", "article_number_2",
    "article_number_3", "color_code", "size_group_code", "size_code",
    "size_name", "currency", "price_buy_gross", "price_buy_net",
    "discount_rate", "price_sell", "material", "target_area",
]
