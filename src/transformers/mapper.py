import logging

from ..exceptions import MappingError
from ..models import MappingRule

logger = logging.getLogger(__name__)


class Mapper:

    def __init__(self, rules: list[MappingRule]) -> None:
        self._rules_by_source: dict[
            tuple[str, ...], dict[str, tuple[str, str]]
        ] = {}
        self._consumed_columns: set[str] = set()

        for rule in rules:
            self._rules_by_source.setdefault(rule.source_columns, {})[rule.source_value] = (
                rule.destination_type,
                rule.destination_value,
            )
            self._consumed_columns.update(rule.source_columns)

    @classmethod
    def from_rows(cls, rows: list[dict[str, str]]) -> "Mapper":
        required_keys = {"source", "destination", "source_type", "destination_type"}
        rules: list[MappingRule] = []

        for i, row in enumerate(rows):
            missing = required_keys - row.keys()
            if missing:
                raise MappingError(
                    f"Mapping row {i + 1} is missing columns: {missing}"
                )

            source_columns = tuple(row["source_type"].split("|"))

            rules.append(
                MappingRule(
                    source_value=row["source"],
                    destination_value=row["destination"],
                    source_columns=source_columns,
                    destination_type=row["destination_type"],
                )
            )

        logger.info("Loaded %d mapping rules across %d source groups",
                    len(rules), len({r.source_columns for r in rules}))
        return cls(rules)

    @property
    def consumed_columns(self) -> frozenset[str]:
        return frozenset(self._consumed_columns)

    def apply(self, row: dict[str, str]) -> dict[str, str]:
        result: dict[str, str] = {}

        for source_cols, lookup_table in self._rules_by_source.items():
            # join with "|" to match the composite key format from mappings CSV (e.g. "EU|38")
            key = "|".join(row.get(col, "") for col in source_cols)

            if key in lookup_table:
                dest_type, dest_value = lookup_table[key]
                result[dest_type] = dest_value
            else:
                logger.debug("No mapping for %s=%r", "+".join(source_cols), key)

        return result
