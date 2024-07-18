from pathlib import Path

import pytest

from bigsky.builders.tycho import parse_float, parse_hip, format_tyc, tycho2_read, StarRow

DATA_PATH = Path(__file__).parent.resolve() / "data"

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


def test_star_row_from_tyc2_dat():
    filename = DATA_PATH / "tyc2.dat"
    rows = [StarRow.from_tyc2(r) for r in tycho2_read(filename)]
    
    assert len(rows) == 3
    assert rows[0].tyc_id == "1-8-1"

    # TODO : more assertions

def test_star_row_from_tyc2_suppl_dat():
    filename = DATA_PATH / "tyc2_suppl.dat"
    rows = [StarRow.from_supp(r) for r in tycho2_read(filename)]
    
    assert len(rows) == 4
    assert rows[3].hip_id == 5413
    assert rows[3].ccdm == "B"

    # TODO : more assertions
