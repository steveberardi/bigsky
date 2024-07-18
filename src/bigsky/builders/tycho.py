import csv
import re
import os
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass

from skyfield.api import Star, load

__version__ = "0.1.0"

"""

    tyc_id: Tycho ID, formatted as a string with hyphens (e.g. 0006-01005-1)
    
    hip_id: Hipparcos ID

    ccdm: CCDM Component Identifier

    magnitude: Visual apparent magnitude, calculated from BT/VT

    bv: BV Color Index

    ra_degrees_j2000: Right Ascension in degrees (0 to 360) and Epoch J2000.0

    dec_degrees_j2000: Declination in degrees (-90 to 90) and Epoch J2000.0

    ra_mas_per_year:

    dec_mas_per_year:

    parallax_mas:

"""


HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve().parent.resolve().parent.resolve()

DATA_PATH = os.environ.get("BIG_SKY_DATA_PATH") or ROOT / "raw"
BUILD_PATH = os.environ.get("BIG_SKY_BUILD_PATH") or ROOT / "build"


planets = load("de421.bsp")
earth = planets["earth"]

ts = load.timescale()


class Epoch:
    J_2000 = ts.tt(2000)
    """Tycho-2 Epoch"""

    J_1991_25 = ts.tt(1991.25)
    """Hipparcos Epoch"""


@dataclass
class StarRow:
    tyc_id: str
    ra_degrees_j2000: float
    dec_degrees_j2000: float
    ra_mas_per_year: float
    dec_mas_per_year: float
    magnitude: float

    hip_id: int = None
    ccdm: str = None
    bv: float = None
    parallax_mas: float = None

    @staticmethod
    def header():
        return [
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

    def to_row(self, r0=2, r1=4):
        def rounded(val, r):
            return round(val, r) if val else val

        return [
            self.tyc_id,
            self.hip_id,
            self.ccdm,
            rounded(self.magnitude, r0),
            rounded(self.bv, r0),
            rounded(self.ra_degrees_j2000, r1),
            rounded(self.dec_degrees_j2000, r1),
            rounded(self.ra_mas_per_year, r1),
            rounded(self.dec_mas_per_year, r1),
            self.parallax_mas,
        ]

    @staticmethod
    def from_tyc2(row):
        def col(i):
            return row[i].strip()

        def col_f(i):
            return parse_float(col(i))

        # Observed RA/DEC
        ra = col_f(24)  # 0-360 deg
        dec = col_f(25)

        if not ra or not dec:
            return None

        ra_mas_per_year = col_f(4)
        dec_mas_per_year = col_f(5)
        ra, dec = to_j2000(ra, dec, ra_mas_per_year, dec_mas_per_year)

        mag_bt = col_f(17)
        mag_vt = col_f(19)
        bv, mag = tycho2_bv_v(mag_bt, mag_vt)

        tyc_id = format_tyc(col(0))
        hip_id = col(23)
        ccdm = None
        if hip_id:
            hip_id, ccdm = parse_hip(hip_id)
            mag = HIP_MAG.get(hip_id) or mag
            parallax_mas = PLX.get(hip_id) or None
        else:
            parallax_mas = PLX.get(tyc_id) or None

        return StarRow(
            tyc_id=tyc_id,
            hip_id=hip_id,
            ccdm=ccdm,
            magnitude=mag,
            bv=bv,
            ra_degrees_j2000=ra,
            dec_degrees_j2000=dec,
            ra_mas_per_year=ra_mas_per_year,
            dec_mas_per_year=dec_mas_per_year,
            parallax_mas=parallax_mas,
        )

    @staticmethod
    def from_supp(row):
        def col(i):
            return row[i].strip()

        def col_f(i):
            return parse_float(col(i))

        ra = col_f(2)  # 0-360 deg
        dec = col_f(3)
        ra_mas_per_year = col_f(4)
        dec_mas_per_year = col_f(5)

        if not ra or not dec:
            return None

        star_kwargs = {}
        if ra_mas_per_year:
            star_kwargs["ra_mas_per_year"] = ra_mas_per_year
        if dec_mas_per_year:
            star_kwargs["dec_mas_per_year"] = dec_mas_per_year

        star = Star(
            ra_hours=ra / 15,
            dec_degrees=dec,
            epoch=Epoch.J_1991_25,
            **star_kwargs,
        )

        _ra, _dec, _distance = earth.at(Epoch.J_2000).observe(star).radec()
        ra = _ra._degrees
        dec = _dec.degrees

        mag_bt = col_f(11)
        mag_vt = col_f(13)
        bv, mag = tycho2_bv_v(mag_bt, mag_vt)

        tyc_id = format_tyc(col(0))
        hip_id = col(17)
        ccdm = None
        if hip_id:
            hip_id, ccdm = parse_hip(hip_id)
            mag = HIP_MAG.get(hip_id) or mag
            parallax_mas = PLX.get(hip_id) or None
        else:
            parallax_mas = PLX.get(tyc_id) or None

        return StarRow(
            tyc_id=tyc_id,
            hip_id=hip_id,
            ccdm=ccdm,
            magnitude=mag,
            bv=bv,
            ra_degrees_j2000=ra,
            dec_degrees_j2000=dec,
            ra_mas_per_year=ra_mas_per_year,
            dec_mas_per_year=dec_mas_per_year,
            parallax_mas=parallax_mas,
        )


def parse_float(n, r=4):
    return round(float(n or 0), r)


def parse_hip(hip) -> tuple[int, str]:
    """
    Parses a HIP ID string into a tuple:

    >>> parse_hip('39825C')
    (39825, 'C')

    - The first element is the HIP id number
    - Second element is the CCDM id (if applicable)

    More info: https://www.cosmos.esa.int/web/hipparcos/double-and-multiple-stars

    """
    try:
        return int(hip), ""
    except:
        hip_id, ccdm, _ = re.split("([A-Z]+)", hip, flags=re.IGNORECASE)

        return int(hip_id), ccdm


def load_hip_magnitudes() -> dict:
    """Returns dictionary where the key is the HIP id and value is its visual magnitude from Tycho-1"""

    hipmags = {}
    with open(DATA_PATH / "tycho-1" / "hip_main.dat", "r") as hipfile:
        reader = csv.reader(hipfile, delimiter="|")

        for row in reader:
            hip = int(row[1].strip())
            mag = parse_float(row[5].strip())
            hipmags[hip] = mag
    return hipmags


def load_tycho1_parallax() -> dict:
    """Returns dictionary where the key is the HIP id and value is its visual magnitude from Tycho-1"""

    parallax = {}
    with open(DATA_PATH / "tycho-1" / "hip_main.dat", "r") as hipfile:
        reader = csv.reader(hipfile, delimiter="|")

        for row in reader:
            hip = int(row[1].strip())
            parallax_mas = parse_float(row[11].strip(), 2)
            parallax[hip] = parallax_mas

    with open(DATA_PATH / "tycho-1" / "tyc_main.dat", "r") as tycfile:
        reader = csv.reader(tycfile, delimiter="|")

        for row in reader:
            tyc = format_tyc(row[1].strip())
            parallax_mas = parse_float(row[11].strip(), 2)
            parallax[tyc] = parallax_mas

    return parallax


def format_tyc(tyc) -> str:
    """
    Formats Tycho ID to its standard designation format: adding hyphens between each TYC number, and removes leading zeroes.

    Examples:
        8479451 -> '8479-45-1'
        008479451 -> '8479-45-1'
    """
    return "-".join([str(int(i)) for i in tyc.split(" ") if i != ""])


def to_j2000(ra_degrees, dec_degrees, ra_mas_per_year, dec_mas_per_year):
    """
    Converts star epoch from J1991.25 (Hipparcos) to J2000

    Returns: ra, dec
    """
    star_kwargs = {}
    if ra_mas_per_year:
        star_kwargs["ra_mas_per_year"] = ra_mas_per_year
    if dec_mas_per_year:
        star_kwargs["dec_mas_per_year"] = dec_mas_per_year

    star = Star(
        ra_hours=ra_degrees / 15,
        dec_degrees=dec_degrees,
        epoch=Epoch.J_1991_25,
        **star_kwargs,
    )

    _ra, _dec, distance = earth.at(Epoch.J_2000).observe(star).radec()
    ra = _ra._degrees
    dec = _dec.degrees

    return ra, dec


def tycho2_bv_v(mag_bt, mag_vt) -> tuple[float, float]:
    """
    Calculates B-V and Johnson V magnitude from Tycho-2 data.

    From Tycho-2 Readme:
        Note (7):
        Blank when no magnitude is available. Either BTmag or VTmag is
        always given. Approximate Johnson photometry may be obtained as:

            V   = VT - 0.090 * (BT-VT)
            B-V = 0.850 * (BT-VT)

        Consult Sect 1.3 of Vol 1 of "The Hipparcos and Tycho Catalogues",
        ESA SP-1200, 1997, for details.
    """

    if mag_bt is None or mag_vt is None:
        return None, mag_vt or mag_bt

    bv = 0.850 * (mag_bt - mag_vt)
    mag = mag_vt - 0.09 * (mag_bt - mag_vt)

    return bv, mag

def tycho2_read(filename):
    with open(filename, "r") as infile:
        reader = csv.reader(infile, delimiter="|")
        for row in reader:
            yield row

def tycho2_rows():
    for t in range(0, 20):
        tycho_file = f"tyc2.dat.{t:02}"
        print(tycho_file)
        yield from tycho2_read(DATA_PATH / "tycho-2" / tycho_file)


PLX = load_tycho1_parallax()
HIP_MAG = load_hip_magnitudes()

if __name__ == "__main__":

    hip_stars = defaultdict(list)

    outfile = open(BUILD_PATH / "tycho2.stars.csv", "w")
    outfile_mag11 = open(BUILD_PATH / "tycho2.stars.mag11.csv", "w")
    
    writer = csv.writer(outfile)
    writer_mag11 = csv.writer(outfile_mag11)

    writer.writerow(StarRow.header())
    writer_mag11.writerow(StarRow.header())

    count = 0
    errors = 0
    no_radec = 0
    tychos = range(0, 20)

    for row in tycho2_rows():
        count += 1

        try:
            output_row = StarRow.from_tyc2(row)

            if output_row is None:
                no_radec += 1
                continue

            writer.writerow(output_row.to_row())

            if output_row.magnitude <= 11:
                writer_mag11.writerow(output_row.to_row())

        except Exception as e:
            print(f"Error on row {str(count+1)}")
            print(e)
            errors += 1
            if errors > 10:
                raise

    with open(DATA_PATH / "tycho-2" / "suppl_1.dat", "r") as supfile:
        reader = csv.reader(supfile, delimiter="|")

        for row in reader:
            count += 1

            try:
                output_row = StarRow.from_supp(row)

                if output_row is None:
                    no_radec += 1
                    continue

                writer.writerow(output_row.to_row())

                if output_row.magnitude <= 11:
                    writer_mag11.writerow(output_row.to_row())

            except Exception as e:
                print(f"Error on row {str(count+1)}")
                print(e)
                errors += 1

    outfile.close()

    print(f"Parsed {count} stars")

    print(f"Skipped {no_radec} no radec")

    print(f"Total Errors: {str(errors)}")
