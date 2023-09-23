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
    hip_id = IntegerField(null=True)


class DeepSkyObject(BaseModel):
    name = CharField()
    ra = FloatField(index=False)
    dec = FloatField(index=False)
    type = CharField()
    magnitude_vt = FloatField(null=True, index=False)
    magnitude_bt = FloatField(null=True, index=False)
    ic = IntegerField(null=True)
    ngc = IntegerField(null=True)
    m = IntegerField(null=True)
    major_ax = FloatField(null=True)
    minor_ax = FloatField(null=True)
    pos_angle = FloatField(null=True)



