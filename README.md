# Fashion Cloud Coding Challenge

Reads a pricat CSV + mappings CSV and outputs a structured JSON catalog.

## Setup

Python 3.10+. No dependencies besides pytest for tests:
```
pip install pytest
```

## Usage

```
python -m src.transform --pricat data/pricat.csv --mappings data/mappings.csv --output output.json
```

Pass `-v` for verbose output (shows row counts, mapping stats, etc).

Field combination (bonus feature):
```
python -m src.transform \
  --pricat data/pricat.csv \
  --mappings data/mappings.csv \
  --output output.json \
  --combine price_buy_net,currency
```
This creates `"price_buy_net_currency": "58.5 EUR"` and removes the originals.

## Tests

```
python -m pytest tests/ -v
```

## Design

Pretty straightforward pipeline -- read CSVs, apply mappings, group into catalog/article/variation, dump JSON.

Code is split into `extractors/`, `transformers/`, and `repositories/`. The mapper reads the mappings CSV and builds lookup tables at runtime so the mapping logic doesn't need to know column names upfront. Two types of mappings:

- Simple: one source column -> one destination (`season: winter` becomes `season: Winter`)
- Composite: multiple columns joined with `|` as lookup key (`size_group_code|size_code: EU|38` becomes `size: European size 38`)

Mapped columns get "consumed" and excluded from output. Whatever's left passes through as-is to the variation.

Some fields like `ean`, `price_buy_net`, `price_sell`, `currency` are typed on the Variation model instead of being generic strings. This is a bit hardcoded -- adding a new special field means touching the model + builder..

## Validation

Not strictly required but I added some basic checks on the model layer since garbage EANs or negative prices would be a pain to debug later:

- **Prices** -- parsed as `Decimal` (not float) and rejects negatives. Unparseable values get logged as warnings and treated as missing
- **Currency** -- checks its a 3 letter uppercase code. Doesn't validate against actual ISO list


## Assumptions

- One brand per pricat file. If multiple brands show up the builder throws an error.
