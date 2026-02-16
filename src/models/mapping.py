from dataclasses import dataclass


@dataclass(frozen=True)
class MappingRule:
    source_value: str
    destination_value: str
    source_columns: tuple[str, ...]
    destination_type: str
