import pandas as pd

from dbdpy.commercial_device import CommercialDevice


class Garmin(CommercialDevice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @classmethod
    def read_file(cls, filepath: str, device_brand: str="Garmin"):
        ...