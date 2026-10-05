import pytest

from src.interpolation import linear_interpolate


def test_midpoint_interpolation():
    result = linear_interpolate(
        x=25,
        x1=20,
        y1=100,
        x2=30,
        y2=140,
    )

    assert result == pytest.approx(120)


def test_non_midpoint_interpolation():
    result = linear_interpolate(
        x=35,
        x1=20,
        y1=0.88,
        x2=40,
        y2=0.93,
    )

    assert result == pytest.approx(0.9175)


def test_interpolation_rejects_duplicate_x_points():
    with pytest.raises(ValueError, match="must be different"):
        linear_interpolate(
            x=20,
            x1=20,
            y1=1.0,
            x2=20,
            y2=1.2,
        )
