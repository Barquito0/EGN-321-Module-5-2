"""Linear interpolation helper for Assignment 3.1."""


def linear_interpolate(x, x1, y1, x2, y2):
    """Return the linearly interpolated y-value at x."""
    if x2 == x1:
        raise ValueError("x1 and x2 must be different for interpolation")

    fraction_between_rows = (x - x1) / (x2 - x1)
    change_in_y = y2 - y1
    return y1 + fraction_between_rows * change_in_y
