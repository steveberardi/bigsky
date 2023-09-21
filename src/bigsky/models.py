from peewee import *

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class Star(BaseModel):
    name = CharField()
    ra = FloatField(index=False)
    dec = FloatField(index=False)
    magnitude = FloatField(index=False)

