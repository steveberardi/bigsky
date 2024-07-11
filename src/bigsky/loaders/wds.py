import csv
import logging

from pathlib import Path

from peewee import *

from bigsky.models import db, Star, DoubleStar
from bigsky.loaders.utils import parse_float, chunker

ROOT = Path(__file__).resolve().parent.resolve().parent.resolve().parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bigsky')

# name = CharField()
#     ra = FloatField(index=False)
#     dec = FloatField(index=False)
#     hip = ForeignKeyField(Star, backref='double_star')
#     wds_id = CharField(unique=True)

# 113 - 130   A18             2000 arcsecond coordinates
# example 000006.64+752859.8
# Columns 113-130:    The hours, minutes, seconds and tenths of seconds (when
#                     known) of Right Ascension for 2000, followed by the degrees,
#                     minutes, and seconds of Declination for 2000, with + and - 
#                     indicating north and south declinations.

def parse_coords(coord_str: str) -> float:
    a, b, c = coord_str[:2], coord_str[2:4], coord_str[4:]
    return parse_float(a) + parse_float(b) / 60 + parse_float(c) / 3600


def load_wds(datapath: str):
    count = 0
    errors = 0
    hips = 0
    filename = "wds_all.txt"
    wds_ids = []
    dupes = []

    logger.info(filename)

    with open(Path(datapath) / "wds" / filename, "r") as infile:

        double_stars = []

        for wds in infile:
            try:
                wds_id = wds[:17].strip()

                if wds_id in wds_ids:
                    # print(f"{wds_id} already parsed, skipping...")
                    # print(wds_id)
                    dupes += wds_id
                    continue
                else:
                    wds_ids.append(wds_id)
                    # continue

                coords = wds[112:129]
                ra_str = coords[:9].strip()
                dec_str = coords[9:].strip()

                ra = parse_coords(ra_str)

                dec = parse_coords(dec_str[1:])
                if dec_str[0] == '-':
                    dec *= -1

                double_stars.append(
                    dict(
                        name=f'double-{str(count)}',
                        ra=ra,
                        dec=dec,
                        wds_id=wds_id
                    )
                )

            except Exception as e:
                print(f"Error on row {str(count+1)}")
                print(e)
                errors += 1
                # raise

            count += 1
        
        # insert records
        for group in chunker(double_stars, 980):
            with db.atomic():
                DoubleStar.insert_many(group).execute()


    logger.info(f"Parsed {count} double stars")
    logger.info(f"Found {hips} hips")
    logger.info(f"Dupes = {len(dupes)}")
    logger.info(f"Total Errors: {str(errors)}")




