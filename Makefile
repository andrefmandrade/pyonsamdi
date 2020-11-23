all: test

test: lint

lint:
	python -m flake8 .
	mypy --ignore-missing-imports .
	black --check .

format:
	black .

.PHONY: lint test all format
