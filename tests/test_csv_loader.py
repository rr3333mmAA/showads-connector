import csv
from pathlib import Path
from src.csv_loader import CsvSource

def write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> Path:
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return path

def test_csv_loader_happy_path(tmp_path):
	path = write_csv(tmp_path / "test.csv", ["Name", "Age", "Cookie", "Banner_id"], [
		{"Name": "John Doe", "Age": "30", "Cookie": "c1", "Banner_id": "5"},
		{"Name": "Jane Doe", "Age": "20", "Cookie": "c2", "Banner_id": "10"},
	])

	source = CsvSource(path=path)
	items = list(source.row())
	assert len(items) == 2
	assert items[0].name == "John Doe"
	assert items[1].banner_id == 10
     
def test_csv_loader_missing_headers(tmp_path):
	path = write_csv(tmp_path / "test.csv", ["Name", "Age"], [
		{"Name": "John Doe", "Age": "30"},
	])

	source = CsvSource(path=path)
	try:
		list(source.row())
		assert False, "expected ValueError for missing headers"
	except ValueError:
		pass