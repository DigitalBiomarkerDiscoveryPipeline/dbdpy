import pandas as pd
import xml.etree.ElementTree as ET

from dbdpy.commercial_device import CommercialDevice
from dbdpy.apple_watch import AppleWatch


class AppleWatch(CommercialDevice):
    def __init__(self,
                 sleep=None,
                 energy=None,
                 steps=None,
                 distance=None,
                 oxygen=None,
                 resting_heart_rate=None,
                 heart_rate=None,
                 respiration_rate=None
                 ) -> None:
        self.sleep = sleep
        self.energy = energy
        self.steps = steps
        self.distance = distance
        self.oxygen = oxygen
        self.resting_heart_rate = resting_heart_rate
        self.heart_rate = heart_rate
        self.respiration_rate = respiration_rate
    
    @classmethod
    def read_file(cls, filepath: str) -> AppleWatch:
        # Extract data from XML file and put into dataframe
        tree = ET.parse(filepath)
        root = tree.getroot()
        record_list = [x.attrib for x in root.iter("Record")]
        record_df = pd.DataFrame(record_list)
        
        # Convert datetime to ISO 8601 format
        datetime_cols = ["creationDate", "startDate", "endDate"]
        record_df[datetime_cols] = record_df[datetime_cols]\
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%Y-%m-%dT%H:%M:%S"))
        
        # Convert values to numeric type
        record_df["value"] = pd.to_numeric(record_df["value"], errors="coerce")
        
        # Shorten observation names
        record_df["type"] = record_df["type"].str.replace("HKQuantityTypeIdentifier", "")
        record_df["type"] = record_df["type"].str.replace("HKCategoryTypeIdentifier", "")

        # Extract data and populate attributes
        energy = record_df[record_df["type"] == "BasalEnergyBurned"]
        steps = record_df[record_df["type"] == "StepCount"]
        distance = record_df[record_df["type"] == "DistanceWalkingRunning"]
        oxygen = record_df[record_df["type"] == "OxygenSaturation"]
        resting_heart_rate = record_df[record_df["type"] == "RestingHeartRate"]
        heart_rate = record_df[record_df["type"] == "HeartRate"]
        respiration_rate = record_df[record_df["type"] == "RespiratoryRate"]
        sleep = record_df[record_df["type"] == "SleepAnalysis"]

        return cls(sleep=sleep, energy=energy, steps=steps, distance=distance, oxygen=oxygen,
                   resting_heart_rate=resting_heart_rate, heart_rate=heart_rate, respiration_rate=respiration_rate)
    