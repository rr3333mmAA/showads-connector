import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CsvSource:
    path: Path

    def load(self) -> list[dict[str, str]]:
        with self.path.open("r") as f:
            reader = csv.DictReader(f)
            return list(reader)
        
if __name__ == "__main__":
    csv_source = CsvSource(Path("data_valid.csv"))
    print(csv_source.load())