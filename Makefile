all: test

test: lint

lint:
	python -m flake8 .
	mypy --ignore-missing-imports .
	black --line-length=130 --check .

format:
	black --line-length=130 .

.PHONY: lint test all format
