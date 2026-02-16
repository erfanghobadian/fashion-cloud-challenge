run:
	python -m src.transform --pricat data/pricat.csv --mappings data/mappings.csv --output output.json

test:
	python -m pytest tests/ -v

mypy:
	python -m mypy src/ tests/
