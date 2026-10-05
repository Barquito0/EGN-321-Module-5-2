"""CSV replay integration from the virtual sensor to Module 3.1."""

from __future__ import annotations

import csv
from pathlib import Path

from src.selection_tool import select_coefficient
from src.sensor_validation import (
    MIN_SUPPORTED_C,
    MAX_SUPPORTED_C,
    SUPPORTED_UNIT,
    evaluate_sensor_reading,
)

DEFAULT_VALVE_FAMILY = "VX-200"


def process_sensor_csv(input_csv, output_log, valve_family=DEFAULT_VALVE_FAMILY):
    """Replay raw sensor rows through validation, filtering, and the original tool.

    Required chain:
    raw sensor -> validation -> accepted/rejected -> value used ->
    original Module 3.1 lookup/interpolation -> coefficient result
    """
    input_csv = Path(input_csv)
    output_log = Path(output_log)

    with input_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    log_rows = []
    previous_valid_temperature = None
    previous_timestamp = None

    for row in rows:
        decision = evaluate_sensor_reading(
            temperature_c=row.get("temperature_c"),
            unit=row.get("unit"),
            timestamp_s=row.get("time_seconds"),
            previous_valid_temperature=previous_valid_temperature,
            previous_timestamp=previous_timestamp,
        )

        accepted_celsius = None
        coefficient = None
        lookup_method = ""
        lower_point = ""
        upper_point = ""
        engineering_status = "NOT_RUN"

        if decision["accepted"]:
            accepted_celsius = decision["accepted_celsius"]

            try:
                result = select_coefficient(valve_family, accepted_celsius)
                coefficient = result["coefficient"]
                lookup_method = result["method"]
                lower_point = result["lower_point"]
                upper_point = result["upper_point"]
                engineering_status = "CALCULATED"
            except ValueError as exc:
                decision = {
                    "accepted": False,
                    "status": "REJECTED",
                    "reason": f"engineering tool refused value: {exc}",
                    "accepted_celsius": None,
                }
                accepted_celsius = None
                engineering_status = "REFUSED"

        try:
            raw_temp = float(row.get("temperature_c"))
            if (
                row.get("unit") == SUPPORTED_UNIT
                and MIN_SUPPORTED_C <= raw_temp <= MAX_SUPPORTED_C
            ):
                previous_valid_temperature = raw_temp
        except (TypeError, ValueError):
            pass

        try:
            current_timestamp = float(row.get("time_seconds"))
            if previous_timestamp is None or current_timestamp > previous_timestamp:
                previous_timestamp = current_timestamp
        except (TypeError, ValueError):
            pass

        log_rows.append(
            {
                "sample_number": row.get("sample_number", ""),
                "timestamp_s": row.get("time_seconds", ""),
                "raw_adc": row.get("raw_adc", ""),
                "raw_temperature_c": row.get("temperature_c", ""),
                "raw_unit": row.get("unit", ""),
                "sensor_source_status": row.get("status", ""),
                "source": row.get("source", ""),
                "validation_status": decision["status"],
                "accepted_celsius": (
                    "" if accepted_celsius is None else f"{accepted_celsius:.1f}"
                ),
                "valve_family": valve_family,
                "engineering_status": engineering_status,
                "coefficient": "" if coefficient is None else f"{coefficient:.6f}",
                "lookup_method": lookup_method,
                "lower_point": lower_point,
                "upper_point": upper_point,
                "reason": decision["reason"],
            }
        )

    fieldnames = list(log_rows[0].keys()) if log_rows else []
    with output_log.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(log_rows)

    return log_rows
