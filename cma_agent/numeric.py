"""Shared parsing and tolerance for typed numeric study answers."""
import math


def parse_number(response):
    cleaned = "".join(str(response).split()).translate(str.maketrans("−", "-", ",$%"))
    try:
        value = float(cleaned)
    except ValueError as exc:
        raise ValueError("Enter a number, such as 1250 or -350.") from exc
    if not math.isfinite(value):
        raise ValueError("Enter a finite number.")
    return value


def within_tolerance(value, expected, tolerance):
    distance = abs(value - expected)
    return distance <= tolerance or (
        tolerance > 0 and math.isclose(distance, tolerance, rel_tol=1e-12)
    )
