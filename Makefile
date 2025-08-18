build:
	docker build -t showads-connector:latest .

run:
	docker run --rm -p 8000:8000 --env-file .env showads-connector:latest

test:
	docker run --rm showads-connector:latest pytest

cli:
	docker run --rm --env-file .env showads-connector:latest python -m src.cli data/data.csv
