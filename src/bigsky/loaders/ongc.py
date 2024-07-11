import csv
from pathlib import Path

from peewee import *

from bigsky.models import db, DeepSkyObject
from bigsky.loaders.utils import parse_float, chunker

filenames = [
    "NGC.csv",
    "addendum.csv",
]

def ra_dec_to_float(ra, dec):
    ra_h, ra_m, ra_s = [float(d) for d in ra.split(":")]
    dec_d, dec_m, dec_s = [float(d) for d in dec.split(":")]

    dec_f = dec_d + (dec_m / 60) + (dec_s / 3600)
    ra_f = ra_h + (ra_m / 60) + (ra_s / 3600)

    return round(ra_f, 6), round(dec_f, 6)

def parse_int(value):
    value = value.strip()
    if value:
        return int(value)
    else:
        return None

def load_ongc(datapath: str):
    count = 0
    errors = 0
    dsos = []
    parsed = {
        'm': set(),
        'ic': set(),
        'ngc': set(),
    }

    for filename in filenames:
        with open(Path(datapath) / "ongc" / filename, "r") as infile:
            reader = csv.DictReader(infile, delimiter=';')

            for row in reader:
                try:
                    desig = row.get("Name").strip()
                    names = (row.get("Common names") or "").split(",")
                    ra, dec = ra_dec_to_float(row.get("RA"), row.get("Dec"))
                    messier = parse_int(row.get("M"))

                    if desig.startswith("IC"):
                        ic = int(desig[2:])
                        ngc = parse_int(row.get("NGC"))
                    elif desig.startswith("NGC"):
                        ngc = int(desig[3:])
                        ic =  parse_int(row.get("IC"))
                    else:
                        print(f"Unknown desig: {desig}")

                    
                    dsos.append(
                        dict(
                            name=names,
                            ra=ra,
                            dec=dec,
                            type=row.get("Type"),
                            magnitude_bt=parse_float(row.get("B-Mag"), r=2),
                            magnitude_vt=parse_float(row.get("V-Mag"), r=2),
                            ic=ic,
                            ngc=ngc,
                            m=messier,
                            major_ax=parse_float(row.get("MajAx"), r=2),
                            minor_ax=parse_float(row.get("MinAx"), r=2),
                            pos_angle=parse_float(row.get("PosAng"), r=2)
                        )
                    )


                except Exception as e:
                    print(f"Error on row {str(count+1)}")
                    print(e)
                    errors += 1

                count += 1
            
            for group in chunker(dsos, 980):
                with db.atomic():
                    DeepSkyObject.insert_many(group).execute()


    print(f"Total Errors: {str(errors)}")
