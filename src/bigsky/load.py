import csv
import sys
from pathlib import Path

from peewee import *

from bigsky.models import db, Star

ROOT = Path(__file__).resolve().parent.resolve().parent.resolve().parent



def init_db(filename: str):
    db.init(filename, pragmas={'journal_mode': 'wal'})
    db.connect()
    db.drop_tables([Star,])
    db.create_tables([Star,])

def parse_float(n, r=4):
    return round(float(n or 0), r)

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))



def load_tycho_2(datapath: str):
    count = 0
    errors = 0
    hips = 0


    tychos = range(0, 19)

    for t in tychos:

        tycho_file = f'tyc2.dat.{t:02}'
        
        print(tycho_file)

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


    print(f"Parsed {count} stars")
    print(f"Found {hips} hips")
    print(f"Total Errors: {str(errors)}")



if __name__ == "__main__":
   raw_data_path = sys.argv[1]
   output_filename = sys.argv[2]

   init_db(output_filename)
   load_tycho_2(raw_data_path)

