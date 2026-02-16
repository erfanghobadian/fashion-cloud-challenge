"""Usage: python -m src.transform --pricat data/pricat.csv --mappings data/mappings.csv --output output.json"""

import argparse
import logging
import sys

from .exceptions import PricatError
from .extractors import CsvReader
from .repositories import JsonCatalogRepository
from .transformers import Builder, FieldCombiner, Mapper


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform a price catalog CSV into structured JSON.",
    )
    parser.add_argument("--pricat", required=True, help="Path to pricat CSV")
    parser.add_argument("--mappings", required=True, help="Path to mappings CSV")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--combine",
        action="append",
        default=[],
        metavar="FIELD1,FIELD2,...",
        help="Combine fields into one (e.g. --combine price_buy_net,currency)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        reader = CsvReader()
        headers, pricat_rows = reader.read(args.pricat)
        _, mapping_rows = reader.read(args.mappings)

        engine = Mapper.from_rows(mapping_rows)

        combiner = None
        if args.combine:
            specs = [FieldCombiner.parse_spec(s) for s in args.combine]
            combiner = FieldCombiner(specs)

        catalog = Builder(engine, combiner).build(headers, pricat_rows)

        JsonCatalogRepository(args.output).save(catalog)

        total = sum(len(a.variations) for a in catalog.articles)
        print(
            f"Wrote {len(catalog.articles)} articles with {total} variations to {args.output}",
            file=sys.stderr,
        )

    except PricatError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
