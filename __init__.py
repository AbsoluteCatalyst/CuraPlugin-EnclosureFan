
from . import EnclosureFans


def getMetaData():
    return {}

def register(app):
    return {"extension": EnclosureFans.EnclosureFans()}
