import csv
import re
import os
from pathlib import Path
from collections import defaultdict

from skyfield.api import Star, load

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


hipmags = load_hip_magnitudes()


def format_tyc(tyc) -> str:
    """
    Formats Tycho ID to its standard designation format: adding hyphens between each TYC number.

    Example: 8479451 -> '8479-45-1'
    """
    return "-".join(tyc.split(" "))


# iterate through all, defer hips to dict (key is hip int)
#   value = [ ["CCDM", ...], ... ]
# iterate through hip dict:
# sort values by CCDM
# first value is primary


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


if __name__ == "__main__":

    hip_stars = defaultdict(list)

    outfile = open(BUILD_PATH / "tycho2.stars.csv", "w")
    writer = csv.writer(outfile)

    writer.writerow(
        [
            "tyc_id",
            "hip_id",
            "ccdm",
            "magnitude",
            "bv",
            "ra_hours_j2000",
            "dec_degrees_j2000",
            "ra_mas_per_year",
            "dec_mas_per_year",
        ]
    )

    count = 0
    errors = 0
    no_radec = 0
    hips = []
    tycho1_ctr = 0
    tychos = range(0, 20)
    mag_max = 0

    for t in tychos:

        tycho_file = f"tyc2.dat.{t:02}"

        print(tycho_file)

        with open(DATA_PATH / "tycho-2" / tycho_file, "r") as infile:
            reader = csv.reader(infile, delimiter="|")

            for row in reader:
                try:
                    tyc = format_tyc(row[0].strip())
                    hip = row[23].strip()
                    tycho1 = row[22].strip()

                    if tycho1:
                        tycho1_ctr += 1
                        # continue

                    # Mean RA/DEC
                    # ra = parse_float(row[2].strip())  # 0-360 deg
                    # dec = parse_float(row[3].strip())

                    # Observed RA/DEC
                    ra = parse_float(row[24].strip())  # 0-360 deg
                    dec = parse_float(row[25].strip())

                    if not ra or not dec:
                        no_radec += 1
                        continue

                    ra_mas_per_year = parse_float(row[4].strip())
                    dec_mas_per_year = parse_float(row[5].strip())
                    ra, dec = to_j2000(ra, dec, ra_mas_per_year, dec_mas_per_year)

                    mag_bt = row[17].strip()
                    mag_vt = row[19].strip()
                    mag = mag_vt or mag_bt

                    if parse_float(mag) > mag_max:
                        mag_max = parse_float(mag)

                    bv = None

                    if mag_bt and mag_vt:
                        #  B-V = 0.850*(BT-VT)
                        bv = 0.850 * (parse_float(mag_bt) - parse_float(mag_vt))

                    if hip:
                        hip, ccdm = parse_hip(hip)
                        mag = hipmags.get(hip) or mag
                        hip_stars[hip].append(
                            [
                                tyc,
                                hip,
                                ccdm,
                                parse_float(mag, 2),
                                parse_float(bv, r=2),
                                parse_float(ra),
                                parse_float(dec),
                                ra_mas_per_year,
                                dec_mas_per_year,
                            ]
                        )
                    else:
                        writer.writerow(
                            [
                                tyc,
                                hip,
                                "",
                                parse_float(mag, 2),
                                parse_float(bv, 2),
                                parse_float(ra),
                                parse_float(dec),
                                ra_mas_per_year,
                                dec_mas_per_year,
                            ]
                        )

                except Exception as e:
                    print(f"Error on row {str(count+1)}")
                    print(e)
                    errors += 1
                    # raise

                count += 1

    with open(DATA_PATH / "tycho-2" / "suppl_1.dat", "r") as supfile:
        reader = csv.reader(supfile, delimiter="|")

        for row in reader:
            try:
                tyc = format_tyc(row[0].strip())
                hip = row[17].strip()

                ra = parse_float(row[2].strip())  # 0-360 deg
                dec = parse_float(row[3].strip())

                ra_mas_per_year = parse_float(row[4].strip())
                dec_mas_per_year = parse_float(row[5].strip())

                if not ra or not dec:
                    no_radec += 1
                    continue

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

                _ra, _dec, distance = earth.at(Epoch.J_2000).observe(star).radec()
                ra = _ra._degrees
                dec = _dec.degrees

                mag_bt = parse_float(row[11].strip())
                mag_vt = parse_float(row[13].strip())

                bv = None

                if mag_bt and mag_vt:
                    # B-V = 0.850*(BT-VT)
                    # V = VT -0.090*(BT-VT)
                    bv = 0.850 * (mag_bt - mag_vt)
                    mag = mag_vt - 0.09 * (mag_bt - mag_vt)
                else:
                    mag = mag_vt or mag_bt

                if hip:
                    hip, ccdm = parse_hip(hip)
                    mag = hipmags.get(hip) or mag
                    hip_stars[hip].append(
                        [
                            tyc,
                            hip,
                            ccdm,
                            parse_float(mag, 2),
                            parse_float(bv, r=2),
                            ra,
                            dec,
                            ra_mas_per_year,
                            dec_mas_per_year,
                        ]
                    )
                else:
                    writer.writerow(
                        [
                            tyc,
                            hip,
                            "",
                            parse_float(mag, 2),
                            parse_float(bv, r=2),
                            ra,
                            dec,
                            ra_mas_per_year,
                            dec_mas_per_year,
                        ]
                    )

                count += 1
            except Exception as e:
                print(f"Error on row {str(count+1)}")
                print(e)
                errors += 1

    hc = 0
    for hip_id, values in hip_stars.items():
        values.sort(key=lambda val: val[2])
        for v in values:
            writer.writerow(v)
            hc += 1

    outfile.close()

    print(f"Parsed {count} stars")
    print(f"... {len(hip_stars.keys())} hips")
    print(f"... {hc} total hips")
    print(f"... {tycho1_ctr} Tycho-1")

    print(f"Skipped {no_radec} no radec")

    print(f"max mag = {mag_max}")
    print(f"Total Errors: {str(errors)}")

    print(hips)
