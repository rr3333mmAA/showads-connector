import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, cast

from .models import Customer


@dataclass(frozen=True)
class CsvSource:
    path: Path

    def row(self) -> Iterator[Customer]:
        with self.path.open("r") as f:
            reader = csv.DictReader(f)
            for row in cast(Iterator[dict[str, str]], reader):
                try:
                    name = str(row["Name"]).strip()
                    age = int(row["Age"])
                    cookie = str(row["Cookie"]).strip()
                    banner_id = int(row["Banner_id"])
                except ValueError as e:
                    raise ValueError(f"Invalid row: {row}") from e

                yield Customer(
                    name=name,
                    age=age,
                    cookie=cookie,
                    banner_id=banner_id,
                )
