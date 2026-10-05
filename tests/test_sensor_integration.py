import pytest

from src.sensor_validation import evaluate_sensor_reading
from src.sensor_integration import process_sensor_csv


def test_normal_sensor_reading_is_accepted():
    d = evaluate_sensor_reading(
        temperature_c=22, unit="C", timestamp_s=1,
        previous_valid_temperature=21, previous_timestamp=0,
    )
    assert d["accepted"] is True


def test_normal_variation_is_accepted():
    d = evaluate_sensor_reading(
        temperature_c=23, unit="C", timestamp_s=2,
        previous_valid_temperature=22, previous_timestamp=1,
    )
    assert d["accepted"] is True


def test_boundary_30_c_is_accepted():
    d = evaluate_sensor_reading(
        temperature_c=30, unit="C", timestamp_s=2,
        previous_valid_temperature=28, previous_timestamp=1,
    )
    assert d["accepted"] is True


def test_out_of_range_is_rejected():
    d = evaluate_sensor_reading(
        temperature_c=60.1, unit="C", timestamp_s=2,
        previous_valid_temperature=25, previous_timestamp=1,
    )
    assert d["status"] == "REJECTED"


def test_suspicious_spike_is_flagged():
    d = evaluate_sensor_reading(
        temperature_c=25, unit="C", timestamp_s=2,
        previous_valid_temperature=19, previous_timestamp=1,
    )
    assert d["status"] == "FLAGGED"


def test_missing_is_rejected():
    d = evaluate_sensor_reading(
        temperature_c="", unit="C", timestamp_s=2,
        previous_valid_temperature=22, previous_timestamp=1,
    )
    assert d["status"] == "REJECTED"


def test_filtering_rule_flags_outside_normal_band():
    d = evaluate_sensor_reading(
        temperature_c=35, unit="C", timestamp_s=2,
        previous_valid_temperature=34, previous_timestamp=1,
    )
    assert d["status"] == "FLAGGED"


def test_unexpected_unit_is_rejected():
    d = evaluate_sensor_reading(
        temperature_c=22, unit="F", timestamp_s=2,
        previous_valid_temperature=21, previous_timestamp=1,
    )
    assert d["status"] == "REJECTED"


def test_stale_timestamp_is_rejected():
    d = evaluate_sensor_reading(
        temperature_c=22, unit="C", timestamp_s=1,
        previous_valid_temperature=21, previous_timestamp=1,
    )
    assert d["status"] == "REJECTED"


def test_valid_sensor_value_flows_through_original_engineering_tool(tmp_path):
    source = tmp_path / "sensor.csv"
    source.write_text(
        "sample_number,time_seconds,raw_adc,temperature_c,unit,status,source\n"
        "1,0.0,557,21.0,C,OK,VELXIO\n",
        encoding="utf-8",
    )
    log = tmp_path / "log.csv"
    rows = process_sensor_csv(source, log, valve_family="VX-200")
    assert rows[0]["validation_status"] == "ACCEPTED"
    assert rows[0]["engineering_status"] == "CALCULATED"
    assert float(rows[0]["coefficient"]) == pytest.approx(1.144)


def test_raw_and_accepted_values_remain_separate(tmp_path):
    source = tmp_path / "sensor.csv"
    source.write_text(
        "sample_number,time_seconds,raw_adc,temperature_c,unit,status,source\n"
        "1,0.0,557,21.0,C,OK,VELXIO\n",
        encoding="utf-8",
    )
    log = tmp_path / "log.csv"
    rows = process_sensor_csv(source, log)
    assert rows[0]["raw_temperature_c"] == "21.0"
    assert rows[0]["accepted_celsius"] == "21.0"
    assert rows[0]["coefficient"] != ""
    assert log.exists()


def test_rejected_value_produces_no_engineering_result(tmp_path):
    source = tmp_path / "sensor.csv"
    source.write_text(
        "sample_number,time_seconds,raw_adc,temperature_c,unit,status,source\n"
        "1,0.0,203,60.1,C,INVALID_OUT_OF_RANGE,VELXIO\n",
        encoding="utf-8",
    )
    log = tmp_path / "log.csv"
    rows = process_sensor_csv(source, log)
    assert rows[0]["validation_status"] == "REJECTED"
    assert rows[0]["accepted_celsius"] == ""
    assert rows[0]["engineering_status"] == "NOT_RUN"
    assert rows[0]["coefficient"] == ""


def test_flagged_change_becomes_next_baseline_but_not_engineering_input(tmp_path):
    source = tmp_path / "sensor.csv"
    source.write_text(
        "sample_number,time_seconds,raw_adc,temperature_c,unit,status,source\n"
        "1,0.0,581,19.0,C,OK,VELXIO\n"
        "2,1.0,512,25.0,C,SUSPICIOUS_CHANGE,VELXIO\n"
        "3,2.0,512,25.0,C,OK,VELXIO\n",
        encoding="utf-8",
    )
    log = tmp_path / "log.csv"
    rows = process_sensor_csv(source, log)
    assert rows[1]["validation_status"] == "FLAGGED"
    assert rows[1]["coefficient"] == ""
    assert rows[2]["validation_status"] == "ACCEPTED"
    assert rows[2]["coefficient"] != ""
