import pytest

from src.selection_tool import select_coefficient


def test_exact_lookup_vx100():
    result = select_coefficient("VX-100", 40)
    assert result["coefficient"] == pytest.approx(0.93)
    assert result["method"] == "exact"


def test_exact_lookup_vx200():
    result = select_coefficient("VX-200", 70)
    assert result["coefficient"] == pytest.approx(1.39)
    assert result["method"] == "exact"


def test_exact_lookup_vx300():
    result = select_coefficient("VX-300", 100)
    assert result["coefficient"] == pytest.approx(1.90)
    assert result["method"] == "exact"


def test_reference_case_vx100_interpolation():
    result = select_coefficient("VX-100", 50)
    assert result["coefficient"] == pytest.approx(0.96)
    assert result["method"] == "interpolation"
    assert result["lower_point"] == (40.0, 0.93)
    assert result["upper_point"] == (60.0, 0.99)


def test_reference_case_vx200_interpolation():
    result = select_coefficient("VX-200", 65)
    assert result["coefficient"] == pytest.approx(1.36)
    assert result["method"] == "interpolation"
    assert result["lower_point"] == (50.0, 1.27)
    assert result["upper_point"] == (70.0, 1.39)


def test_reference_case_vx300_interpolation():
    result = select_coefficient("VX-300", 62.5)
    assert result["coefficient"] == pytest.approx(1.63)
    assert result["method"] == "interpolation"
    assert result["lower_point"] == (50.0, 1.55)
    assert result["upper_point"] == (75.0, 1.71)


def test_lower_boundary_accepted():
    result = select_coefficient("VX-100", 20)
    assert result["coefficient"] == pytest.approx(0.88)
    assert result["method"] == "exact"
    assert result["supported_range"] == (20.0, 100.0)


def test_upper_boundary_accepted():
    result = select_coefficient("VX-300", 125)
    assert result["coefficient"] == pytest.approx(2.12)
    assert result["method"] == "exact"
    assert result["supported_range"] == (25.0, 125.0)


def test_below_range_refused():
    with pytest.raises(ValueError, match="supported minimum"):
        select_coefficient("VX-100", 5)


def test_above_range_refused():
    with pytest.raises(ValueError, match="supported maximum"):
        select_coefficient("VX-200", 95)


def test_vx300_below_range_refused():
    with pytest.raises(ValueError, match="supported minimum"):
        select_coefficient("VX-300", 20)


def test_vx300_above_range_refused():
    with pytest.raises(ValueError, match="supported maximum"):
        select_coefficient("VX-300", 130)


def test_unknown_family_refused():
    with pytest.raises(ValueError, match="Unsupported valve_family"):
        select_coefficient("VX-999", 50)


def test_interpolation_result_explains_how_value_was_produced():
    result = select_coefficient("VX-200", 65)

    assert result == {
        "valve_family": "VX-200",
        "temperature_c": 65,
        "coefficient": pytest.approx(1.36),
        "method": "interpolation",
        "lower_point": (50.0, 1.27),
        "upper_point": (70.0, 1.39),
        "supported_range": (10.0, 90.0),
    }
