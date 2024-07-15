import pytest


from bigsky.parsers.tycho2 import parse_float


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
