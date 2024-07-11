import csv
import logging

from pathlib import Path

from peewee import *

from bigsky.models import db, Star
from bigsky.loaders.utils import parse_float, chunker

ROOT = Path(__file__).resolve().parent.resolve().parent.resolve().parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bigsky')

def ra_dec_to_float(ra, dec):
    ra_h, ra_m, ra_s = [float(d) for d in ra.split(" ")]
    dec_d, dec_m, dec_s = [float(d) for d in dec.split(" ")]

    dec_f = dec_d + (dec_m / 60) + (dec_s / 3600)
    ra_f = ra_h + (ra_m / 60) + (ra_s / 3600)

    return round(ra_f, 6), round(dec_f, 6)


def parse_float(n, r=4):
    return round(float(n or 0), r)

def load_tycho_1(datapath: str):
    count = 0
    errors = 0
    hips = 0

    with open(Path(datapath) / "tycho-1" / "tyc_main.dat", "r") as infile:
        reader = csv.reader(infile, delimiter='|')

        stars = []

        for row in reader:
            try:
                hip = row[31].strip()
                ra, dec = ra_dec_to_float(row[3], row[4])
                mag = row[5].strip() or row[34].strip() or row[32].strip()
                if hip:
                    hips += 1

                stars.append(
                    dict(
                        name=f'star-{str(count)}',
                        ra=ra,
                        dec=dec,
                        magnitude=parse_float(mag, r=2),
                        hip_id=hip,
                        bv=parse_float(row[37].strip(), r=2),
                    )
                )

            except Exception as e:
                print(f"Error on row {str(count+1)}")
                print(e)
                errors += 1
                raise

            count += 1
        
        for group in chunker(stars, 980):
            with db.atomic():
                Star.insert_many(group).execute()


    print(f"Parsed {count} stars")
    print(f"{hips} hips")
    print(f"Total Errors: {str(errors)}")
