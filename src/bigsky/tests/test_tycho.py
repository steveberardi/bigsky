from pathlib import Path

import pytest

from bigsky.builders.tycho import (
    parse_float,
    parse_hip,
    format_tyc,
    tycho2_read,
    StarRow,
)

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


def test_star_row_header():
    assert StarRow.header() == [
        "tyc_id",
        "hip_id",
        "ccdm",
        "magnitude",
        "bv",
        "ra_degrees_j2000",
        "dec_degrees_j2000",
        "ra_mas_per_year",
        "dec_mas_per_year",
        "parallax_mas",
    ]


def test_star_row_from_tyc2_dat():
    filename = DATA_PATH / "tyc2.dat"
    rows = [StarRow.from_tyc2(r) for r in tycho2_read(filename)]

    assert len(rows) == 3

    assert rows[0].to_row() == [
        "1-8-1",
        "",
        None,
        12.15,
        0.0,
        2.3175,
        2.2319,
        -16.3,
        -9.0,
        None,
    ]


def test_star_row_from_tyc2_suppl_dat():
    filename = DATA_PATH / "tyc2_suppl.dat"
    rows = [StarRow.from_supp(r) for r in tycho2_read(filename)]

    assert len(rows) == 4
    assert rows[3].to_row() == [
        "22-341-2",
        5413,
        "B",
        9.27,
        -10.07,
        17.3031,
        2.5526,
        -7.8,
        -28.5,
        1.77,
    ]
