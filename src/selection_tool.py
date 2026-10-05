"""
Validated lookup and interpolation tool for valve coefficients.

Engineering rule:
Interpolate inside the evidence. Refuse outside it.
"""

from src.interpolation import linear_interpolate
from src.lookup_tables import LOOKUP_TABLES


def select_coefficient(valve_family, temperature_c):
    """
    Select or interpolate a valve coefficient.

    Parameters
    ----------
    valve_family : str
        Supported valve family name.
    temperature_c : int or float
        Requested operating temperature in degrees Celsius.

    Returns
    -------
    dict
        Structured information describing the lookup result.

    Raises
    ------
    ValueError
        If the valve family is unsupported or the requested temperature is
        outside that family's supported engineering-data range.
    """

    if valve_family not in LOOKUP_TABLES:
        raise ValueError(f"Unsupported valve_family: {valve_family}")

    table = LOOKUP_TABLES[valve_family]

    minimum_temp = table[0][0]
    maximum_temp = table[-1][0]
    supported_range = (minimum_temp, maximum_temp)

    if temperature_c < minimum_temp:
        raise ValueError(
            f"temperature_c {temperature_c} is below the supported minimum "
            f"{minimum_temp} for {valve_family}"
        )

    if temperature_c > maximum_temp:
        raise ValueError(
            f"temperature_c {temperature_c} exceeds the supported maximum "
            f"{maximum_temp} for {valve_family}"
        )

    for point in table:
        point_temperature, point_coefficient = point

        if temperature_c == point_temperature:
            return {
                "valve_family": valve_family,
                "temperature_c": temperature_c,
                "coefficient": point_coefficient,
                "method": "exact",
                "lower_point": point,
                "upper_point": point,
                "supported_range": supported_range,
            }

    for index in range(len(table) - 1):
        lower_point = table[index]
        upper_point = table[index + 1]

        lower_temp, lower_coefficient = lower_point
        upper_temp, upper_coefficient = upper_point

        if lower_temp < temperature_c < upper_temp:
            coefficient = linear_interpolate(
                x=temperature_c,
                x1=lower_temp,
                y1=lower_coefficient,
                x2=upper_temp,
                y2=upper_coefficient,
            )

            return {
                "valve_family": valve_family,
                "temperature_c": temperature_c,
                "coefficient": coefficient,
                "method": "interpolation",
                "lower_point": lower_point,
                "upper_point": upper_point,
                "supported_range": supported_range,
            }

    raise RuntimeError(
        "Unable to locate surrounding lookup rows for an in-range temperature"
    )
