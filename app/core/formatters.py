"""Common display formatters used by UI and export layers."""


def format_score(value: float) -> str:
    """Format score-like numeric values for display.

    Whole-number floats are displayed without the redundant decimal part,
    while non-integers keep one decimal place.
    """
    if float(value).is_integer():
        return str(int(value))

    return f"{value:.1f}"
