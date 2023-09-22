import csv
import logging

from pathlib import Path

from peewee import *

from bigsky.models import db, Star
from bigsky.loaders.utils import parse_float, chunker

ROOT = Path(__file__).resolve().parent.resolve().parent.resolve().parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bigsky')

def load_tycho_2(datapath: str):
    count = 0
    errors = 0
    hips = 0
    tychos = range(0, 19)

    for t in tychos:

        tycho_file = f'tyc2.dat.{t:02}'
        
        logger.info(tycho_file)

        with open(Path(datapath) / "tycho-2" / tycho_file, "r") as infile:
            reader = csv.reader(infile, delimiter='|')

            stars = []
            for row in reader:
                try:
                    hip = row[23].strip()
                    if hip:
                        hips += 1

                    ra = parse_float(row[2].strip())
                    dec = parse_float(row[3].strip())
                    mag = parse_float(row[19].strip() or row[17].strip())

                    stars.append(
                        dict(
                            name=f'star-{str(count)}',
                            ra=ra,
                            dec=dec,
                            magnitude=mag,
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


    logger.info(f"Parsed {count} stars")
    logger.info(f"Found {hips} hips")
    logger.info(f"Total Errors: {str(errors)}")




