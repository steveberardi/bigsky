from peewee import *

from bigsky.models import db, Star, DeepSkyObject, DoubleStar


def init_db(filename: str):
    db.init(filename, pragmas={"journal_mode": "wal"})
    db.connect()
    db.drop_tables([Star, DeepSkyObject, DoubleStar])
    db.create_tables([Star, DeepSkyObject, DoubleStar])


def parse_float(n, r=4):
    return round(float(n or 0), r)


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
