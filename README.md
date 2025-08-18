## ShowAds Connector

A small CLI and REST API that reads a CSV of customers, applies optional age limits, and sends valid customers to ShowAds.

### Requirements
- Docker (for containerized run)
- Make (optional, for shortcuts)
- Or Python 3.12+ for local (non-Docker) usage

### Environment variables
Create a `.env` file at least with `SHOWADS_BASE_URL` (see `.env.example`).
The app reads configuration from environment variables:
- `SHOWADS_BASE_URL` (required)
- `SHOWADS_PROJECT_KEY` (default: dev-key)
- `MIN_BANNER_ID` (default: 1)
- `MAX_BANNER_ID` (default: 99)
- `TOKEN_EXPIRY_SECONDS` (default: 84600)
- `MAX_RETRIES` (default: 5)
- `RETRY_BACKOFF_SECONDS` (default: 2)
- `BULK_BATCH_SIZE` (default: 1000)

### Using Make (shortcuts)
- `make build`: build the Docker image `showads-connector:latest`.
- `make run`: start the API on port 8000 using variables from `.env`.
- `make cli`: run the CLI inside the container against `data/data.csv`.
- `make test`: run the test suite inside the container.

### Without Make (direct Docker)
- Build the image:
```
docker build -t showads-connector:latest .
```
- Run the API (serves FastAPI on http://localhost:8000):
```
docker run --rm -p 8000:8000 --env-file .env showads-connector:latest
```
- Run the CLI against the included sample file:
```
docker run --rm --env-file .env showads-connector:latest python -m src.cli data/data.csv
```
- Run tests:
```
docker run --rm showads-connector:latest pytest
```

### Local install (no Docker)
1) Create and activate a virtualenv, then install deps:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Export the required variables (or wrap commands with `env $(cat .env | xargs)`):
```
export SHOWADS_BASE_URL=https://api.showads.example
export SHOWADS_PROJECT_KEY=dev-key
export MIN_BANNER_ID=1
export MAX_BANNER_ID=99
export TOKEN_EXPIRY_SECONDS=84600
export MAX_RETRIES=5
export RETRY_BACKOFF_SECONDS=2
export BULK_BATCH_SIZE=1000
```
3) Run the CLI with your CSV:
```
python -m src.cli path/to/your.csv --age-limit 18 65
```
4) Or run the API locally on port 8000:
```
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### API endpoints
- `GET /health`: health check
- `GET /config/age-limit`: get the current age limit
- `PUT /config/age-limit`: set the age limit
- `POST /process/csv`: process a CSV file

API file processing example:
```
curl -X POST http://localhost:8000/process/csv \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your.csv"
```

### CLI usage
```
python -m src.cli CSV_PATH [--age-limit MIN MAX]
```
Examples:
```
python -m src.cli data/data.csv
python -m src.cli data/data.csv --age-limit 21 60
```

### Notes
- Sample CSVs are in `data/`.

### Future improvements
- Multi-threading for processing CSV file
- Return messages for invalid customers in API response