import unicodedata

import pandas as pd
import xml.etree.ElementTree as ET

from dbdpy.commercial_device import CommercialDevice


class AppleWatch(CommercialDevice):
    def __init__(self,
                 sleep=None,
                 energy=None,
                 steps=None,
                 distance=None,
                 oxygen=None,
                 heart_rate=None
                 ) -> None:
        self.sleep = sleep
        self.energy = energy
        self.steps = steps
        self.distance = distance
        self.oxygen = oxygen
        self.heart_rate = heart_rate
    
    @classmethod
    def read_file(cls, filepath: str, device_name: str="Apple Watch"):
        # TODO: Deidentify device name
        # TODO: Store device model information
        # Extract data from XML file and put into dataframe
        tree = ET.parse(filepath)
        root = tree.getroot()
        record_list = [x.attrib for x in root.iter("Record")]
        record_df = pd.DataFrame(record_list)

        # Only save the watch data and discard the iPhone data
        record_df["sourceName"] = record_df["sourceName"].apply(lambda x: unicodedata.normalize("NFKC", x))
        record_df = record_df[record_df["sourceName"].str.contains(device_name)]

        # Drop columns that will not be used
        drop_cols = ["sourceName", "sourceVersion", "unit", "creationDate", "device"]
        record_df.drop(columns=drop_cols, axis=1, inplace=True)

        # Convert datetime to ISO 8601 format
        datetime_cols = ["startDate", "endDate"]
        record_df[datetime_cols] = record_df[datetime_cols]\
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%Y-%m-%dT%H:%M:%S"))
        
        # Convert values to numeric type
        record_df["value"] = pd.to_numeric(record_df["value"], errors="coerce")
        
        # Shorten observation names
        record_df["type"] = record_df["type"].str.replace("HKQuantityTypeIdentifier", "")
        record_df["type"] = record_df["type"].str.replace("HKCategoryTypeIdentifier", "")

        # Extract data, convert to standard format, and populate attributes
        energy = record_df[record_df["type"] == "BasalEnergyBurned"]\
            .drop(columns="type").rename(columns={"value": "active_calories"})
        steps = record_df[record_df["type"] == "StepCount"]\
            .drop(columns="type").rename(columns={"value": "steps"})
        distance = record_df[record_df["type"] == "DistanceWalkingRunning"]\
            .drop(columns="type").rename(columns={"value": "distance"})
        oxygen = record_df[record_df["type"] == "OxygenSaturation"]\
            .drop(columns="type").rename(columns={"value": "SpO2"})
        heart_rate = record_df[record_df["type"] == "HeartRate"]\
            .drop(columns="type").rename(columns={"value": "heart_rate"})
        sleep = record_df[record_df["type"] == "SleepAnalysis"]\
            .drop(columns="type")

        return cls(sleep=sleep, energy=energy, steps=steps, distance=distance, oxygen=oxygen,
                   heart_rate=heart_rate)
    