import pytest


from bigsky.builders.tycho import parse_float, parse_hip, format_tyc


@pytest.mark.parametrize(
    "value,r,expected",
    [
        ("4.56789", 4, 4.5679),
        ("4.56789", 2, 4.57),
        ("4.56789", 1, 4.6),
        ("4.56789", 0, 5),
    ],
)
def test_parse_float(value, r, expected):
    assert parse_float(value, r) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("123", (123, "")),
        ("123A", (123, "A")),
        ("123AB", (123, "AB")),
        ("123C", (123, "C")),
    ],
)
def test_parse_hip(value, expected):
    assert parse_hip(value) == expected



@pytest.mark.parametrize(
    "value,expected",
    [
        ("4901 00455 1", "4901-455-1"),
        ("0598 00895 1", "598-895-1"),
    ],
)
def test_format_tyc(value, expected):
    assert format_tyc(value) == expected
