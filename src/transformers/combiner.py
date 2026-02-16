import logging

logger = logging.getLogger(__name__)


class FieldCombiner:

    def __init__(self, specs: list[list[str]]) -> None:
        self._specs = specs

    @staticmethod
    def parse_spec(spec_string: str) -> list[str]:
        return [f.strip() for f in spec_string.split(",") if f.strip()]

    @staticmethod
    def make_combined_key(fields: list[str]) -> str:
        return "_".join(fields)

    def combine(self, variation: dict[str, str]) -> dict[str, str]:
        result = dict(variation)

        for fields in self._specs:
            values = [result.get(f, "") for f in fields]
            if all(values):
                combined_key = self.make_combined_key(fields)
                for f in fields:
                    result.pop(f, None)
                result[combined_key] = " ".join(values)
            else:
                missing = [f for f, v in zip(fields, values) if not v]
                logger.debug("Skipping combine for %s: missing fields %s",
                            "+".join(fields), missing)

        return result
