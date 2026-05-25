from app.core.formatters import format_score


def test_format_score_hides_redundant_decimal_for_whole_numbers():
    assert format_score(5.0) == "5"
    assert format_score(10.0) == "10"


def test_format_score_keeps_one_decimal_for_non_whole_numbers():
    assert format_score(9.5) == "9.5"
    assert format_score(8.7) == "8.7"
