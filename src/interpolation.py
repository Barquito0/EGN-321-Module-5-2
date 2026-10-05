"""
Linear interpolation helper for Assignment 3.1.
"""


def linear_interpolate(x, x1, y1, x2, y2):
    """
    Return the linearly interpolated y-value at x.

    Parameters
    ----------
    x : int or float
        Requested x-value.
    x1 : int or float
        Lower known x-value.
    y1 : int or float
        Known y-value at x1.
    x2 : int or float
        Upper known x-value.
    y2 : int or float
        Known y-value at x2.

    Returns
    -------
    float
        Interpolated y-value.

    Notes
    -----
    This helper only performs interpolation math. It does not decide whether
    x is inside an engineering-supported range. Range validation belongs in
    selection_tool.py.
    """
    if x2 == x1:
        raise ValueError("x1 and x2 must be different for interpolation")

    fraction_between_rows = (x - x1) / (x2 - x1)
    change_in_y = y2 - y1

    return y1 + fraction_between_rows * change_in_y
