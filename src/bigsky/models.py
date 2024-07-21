from peewee import *

db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Star(BaseModel):
    name = CharField()
    ra = FloatField(index=False)
    dec = FloatField(index=False)
    bayer = CharField(null=True)
    magnitude = FloatField(index=False)
    magnitude_vt = FloatField(null=True, index=False)
    magnitude_bt = FloatField(null=True, index=False)
    bv = FloatField(null=True, index=False)
    hip_id = IntegerField(unique=False, null=True)


class DeepSkyObject(BaseModel):
    name = CharField()
    ra = FloatField(index=False)
    dec = FloatField(index=False)
    type = CharField()
    magnitude_vt = FloatField(null=True, index=False)
    magnitude_bt = FloatField(null=True, index=False)
    major_ax = FloatField(null=True)
    minor_ax = FloatField(null=True)
    pos_angle = FloatField(null=True)

    # Identifier Fields
    ic = IntegerField(unique=False, null=True)
    ngc = IntegerField(unique=False, null=True)
    m = IntegerField(unique=False, null=True)


class DoubleStar(BaseModel):
    name = CharField()
    ra = FloatField(index=False)
    dec = FloatField(index=False)
    hip = ForeignKeyField(Star, backref="double_star", null=True)
    wds_id = CharField(unique=True, null=True)
