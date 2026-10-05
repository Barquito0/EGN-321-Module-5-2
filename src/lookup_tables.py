"""
EGN 321 — Module 3, Assignment 3.1
Readable engineering lookup-table data.

The authoritative values come from data/valve_lookup_table.csv.
"""

import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "valve_lookup_table.csv"


def _load_lookup_tables():
    """Load and group the engineering lookup data by valve family."""
    tables = {}
    with DATA_FILE.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            valve_family = row["valve_family"]
            temperature_c = float(row["temperature_c"])
            coefficient = float(row["coefficient"])
            tables.setdefault(valve_family, []).append(
                (temperature_c, coefficient)
            )

    for table in tables.values():
        table.sort(key=lambda point: point[0])

    return tables


LOOKUP_TABLES = _load_lookup_tables()
