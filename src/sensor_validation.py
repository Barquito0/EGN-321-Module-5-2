"""Sensor validation and Assignment 5.1 filtering for Assignment 5.2."""

from __future__ import annotations
import math

SUPPORTED_UNIT = "C"
MIN_SUPPORTED_C = 0.0
MAX_SUPPORTED_C = 50.0
MIN_NORMAL_C = 18.0
MAX_NORMAL_C = 30.0
MAX_CHANGE_C = 3.0


def _finite_float(name, value):
    if value is None or value == "":
        raise ValueError(f"{name} is missing")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def evaluate_sensor_reading(
    *,
    temperature_c,
    unit,
    timestamp_s,
    previous_valid_temperature=None,
    previous_timestamp=None,
):
    """Validate and filter one raw sensor reading before engineering use."""
    if unit != SUPPORTED_UNIT:
        return {
            "accepted": False,
            "status": "REJECTED",
            "reason": f"unexpected unit: expected C, received {unit!r}",
            "accepted_celsius": None,
        }

    try:
        timestamp = _finite_float("timestamp_s", timestamp_s)
    except ValueError as exc:
        return {
            "accepted": False,
            "status": "REJECTED",
            "reason": str(exc),
            "accepted_celsius": None,
        }

    if previous_timestamp is not None and timestamp <= float(previous_timestamp):
        return {
            "accepted": False,
            "status": "REJECTED",
            "reason": "stale or non-increasing timestamp",
            "accepted_celsius": None,
        }

    try:
        temp = _finite_float("temperature_c", temperature_c)
    except ValueError as exc:
        return {
            "accepted": False,
            "status": "REJECTED",
            "reason": str(exc),
            "accepted_celsius": None,
        }

    if temp < MIN_SUPPORTED_C or temp > MAX_SUPPORTED_C:
        return {
            "accepted": False,
            "status": "REJECTED",
            "reason": "outside supported 0-50 C sensor range",
            "accepted_celsius": None,
        }

    if temp < MIN_NORMAL_C or temp > MAX_NORMAL_C:
        return {
            "accepted": False,
            "status": "FLAGGED",
            "reason": "outside expected 18-30 C normal sensor range",
            "accepted_celsius": None,
        }

    if (
        previous_valid_temperature is not None
        and abs(temp - float(previous_valid_temperature)) > MAX_CHANGE_C
    ):
        return {
            "accepted": False,
            "status": "FLAGGED",
            "reason": "change greater than 3 C from previous valid reading",
            "accepted_celsius": None,
        }

    return {
        "accepted": True,
        "status": "ACCEPTED",
        "reason": "sensor reading passed validation and filtering",
        "accepted_celsius": temp,
    }
