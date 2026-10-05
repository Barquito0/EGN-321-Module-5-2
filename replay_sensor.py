"""Run Assignment 5.2 CSV replay through the Module 3.1 valve tool."""

from pathlib import Path
from src.sensor_integration import process_sensor_csv

INPUT = Path("data/sensor_readings_raw.csv")
OUTPUT = Path("sensor_integration_log.csv")

rows = process_sensor_csv(INPUT, OUTPUT, valve_family="VX-200")

accepted = sum(r["validation_status"] == "ACCEPTED" for r in rows)
flagged = sum(r["validation_status"] == "FLAGGED" for r in rows)
rejected = sum(r["validation_status"] == "REJECTED" for r in rows)
calculated = sum(r["engineering_status"] == "CALCULATED" for r in rows)

print(f"Processed: {len(rows)}")
print(f"Accepted: {accepted}")
print(f"Flagged: {flagged}")
print(f"Rejected: {rejected}")
print(f"Engineering results: {calculated}")
print(f"Trace log: {OUTPUT}")
