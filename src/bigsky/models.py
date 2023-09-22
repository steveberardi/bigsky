from peewee import *

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class Star(BaseModel):
    name = CharField()
    bayer = CharField(null=True)
    ra = FloatField(index=False)
    dec = FloatField(index=False)
    magnitude = FloatField(index=False)
    magnitude_vt = FloatField(null=True, index=False)
    magnitude_bt = FloatField(null=True, index=False)
    hip_id = IntegerField(null=True)


