import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from garmin_fit_sdk import Decoder, Stream, Profile
import datetime

# from device import CommercialDevice


# class garmin(CommercialDevice):
class garmin:
    def __init__(self):
        # super().__init__('garmin')
        self.messages = None

    # helper functions
    def convert_time(self, df):
        df["timestamp"] = [
            datetime.datetime.utcfromtimestamp(631065600 + df["timestamp"][i])
            - datetime.timedelta(hours=4)
            for i in range(len(df["timestamp"]))
        ]
        return df

    def get_timestamp(self, df):
        for i in range(len(df) - 1):
            if df.iloc[i, 0].astype(str) == "nan":
                timestamp_16 = df["timestamp_16"][i]
                df.iloc[i, 0] = df.iloc[(i - 1), 0]

        for i in range(len(df)):
            mesgTimestamp = int(df["timestamp"][i])
            try:
                timestamp_16 = int(df["timestamp_16"][i])
                duration = (timestamp_16 - (mesgTimestamp & 0xFFFF)) & 0xFFFF
            except ValueError:
                continue
            mesgTimestamp += duration
            df.iloc[i, 0] = mesgTimestamp
        return df

    @classmethod
    def from_directory(cls, filepath):
        newGarmin = cls()
        file_type = filepath.split(".")[-1]
        if file_type == "fit":
            data = newGarmin.read_fit(filepath)
        else:
            data = newGarmin.read_sleepData(filepath)
        newobject = cls(data)
        return newobject

    # read wellness file
    def read_fit(self, path):
        """
        Reads FIT file and stores the data in the class instance.

        Args:
            path (str): The path to the FIT file to be read.
        """
        stream = Stream.from_file(path)
        decoder = Decoder(stream)
        messages, errors = decoder.read(
            apply_scale_and_offset=True,
            convert_datetimes_to_dates=False,
            convert_types_to_strings=True,
            enable_crc_check=True,
            expand_sub_fields=True,
            expand_components=True,
            merge_heart_rates=False,
            mesg_listener=None,
        )

        self.messages = messages

    # read sleep data json file
    def read_sleepData(self, path):
        """
        Reads sleep data in json file and stores the data in the class instance.

        Args:
            file (str): The path to the json file to be read.
        """
        sleepData = pd.read_json(path)
        sleepData["sleepStartTimestampGMT"] = pd.to_datetime(
            sleepData["sleepStartTimestampGMT"]
        )
        sleepData["sleepStartTimestampGMT"] = sleepData[
            "sleepStartTimestampGMT"
        ] - datetime.timedelta(hours=4)
        sleepData["sleepEndTimestampGMT"] = pd.to_datetime(
            sleepData["sleepEndTimestampGMT"]
        )
        sleepData["sleepEndTimestampGMT"] = sleepData[
            "sleepEndTimestampGMT"
        ] - datetime.timedelta(hours=4)
        sleepData["calendarDate"] = pd.to_datetime(sleepData["calendarDate"])
        sleepData.drop(
            sleepData[sleepData["sleepWindowConfirmationType"] == "UNCONFIRMED"].index,
            inplace=True,
        )
        self.sleepData = sleepData

    # get sleep stage information
    def get_sleepstage(self):
        sleepStage = self.sleepData[
            [
                "calendarDate",
                "deepSleepSeconds",
                "lightSleepSeconds",
                "remSleepSeconds",
                "awakeSleepSeconds",
            ]
        ]
        return sleepStage

    # get raw wellness data
    def get_raw_data(self):
        raw_data = pd.DataFrame(self.messages["monitoring_mesgs"])
        raw_data = self.get_timestamp(raw_data)
        raw_data = self.convert_time(raw_data)
        return raw_data

    def get_stress_level(self):
        stress = pd.DataFrame(self.messages["stress_level_mesgs"])
        stress["stress_level_time"] = [
            datetime.datetime.utcfromtimestamp(
                631065600 + stress["stress_level_time"][i]
            )
            - datetime.timedelta(hours=4)
            for i in range(len(stress["stress_level_time"]))
        ]
        return stress

    def get_SpO2(self):
        SpO2 = pd.DataFrame(self.messages["spo2_data_mesgs"])
        SpO2 = self.convert_time(SpO2)
        return SpO2

    def get_floor(self):
        raw_data = self.get_raw_data()
        floor = raw_data[["timestamp", "ascent", "descent"]]
        floor.iloc[0, 1:] = 0
        for i in range(len(floor) - 1):
            if str(floor["ascent"][i + 1]) == "nan":
                floor.iloc[i + 1, 1] = floor.iloc[i, 1]
            else:
                floor.iloc[i + 1, 1] += floor.iloc[i, 1]

            if str(floor["descent"][i + 1]) == "nan":
                floor.iloc[i + 1, 2] = floor.iloc[i, 2]
            else:
                floor.iloc[i + 1, 2] += floor.iloc[i, 2]

        duplicate_rows = floor[floor.duplicated()]
        floor_no_duplicates = floor.drop_duplicates(keep="first")

        return floor_no_duplicates

    def get_distance(self):
        raw_data = self.get_raw_data()
        distance = raw_data.iloc[:-5, :]
        distance = distance[["timestamp", "distance"]]
        distance.iloc[0, 1] = 0
        for i in range(len(distance) - 1):
            i = i + 1
            if str(distance["distance"][i]) == "nan":
                if str(distance["distance"][i - 1]) != "nan":
                    distance.iloc[i, 1] = distance["distance"][i - 1]

            if distance.iloc[i, 1] < distance["distance"][i - 1]:
                distance.iloc[i, 1] = distance["distance"][i - 1]

        duplicate_rows = distance[distance.duplicated()]
        distance_no_duplicates = distance.drop_duplicates(keep="first")

        return distance_no_duplicates

    def get_hr(self):
        raw_data = self.get_raw_data()
        hr_df = raw_data[~raw_data["heart_rate"].isna()].reset_index(drop=True)
        hr_df = hr_df[["timestamp", "heart_rate"]]
        hr_df["heart_rate"] = hr_df["heart_rate"].astype(int)
        return hr_df

    def get_intensity(self):
        raw_data = self.get_raw_data()
        intensity = raw_data[~raw_data["intensity"].isna()].reset_index(drop=True)
        intensity = intensity[["timestamp", "intensity"]]
        return intensity

    def get_calories(self):
        raw_data = self.get_raw_data()
        calories = raw_data.iloc[:-5, :]
        calories = calories[["timestamp", "active_calories"]]
        for i in range(len(calories) - 1):
            if (
                str(calories["active_calories"][i + 1]) == "nan"
                or calories["active_calories"][i + 1] < calories["active_calories"][i]
            ):
                calories.iloc[i + 1, 1] = calories.iloc[i, 1]

        duplicate_rows = calories[calories.duplicated()]
        calories_no_duplicates = calories.drop_duplicates(keep="first")

        return calories_no_duplicates

    def get_sleep_time(self):
        sleep = pd.DataFrame(self.messages["sleep_level_mesgs"])
        sleep = self.convert_time(sleep)
        for i in range(len(sleep["timestamp"]) - 1):
            time_difference = sleep["timestamp"][i + 1] - sleep["timestamp"][i]
            if time_difference.seconds // 3600 > 1:
                sleep_time = sleep["timestamp"][i]
                wake_time = sleep["timestamp"][i + 1]

        return sleep_time, wake_time

    def get_rhr(self):
        rhr_df = pd.DataFrame(self.messages["monitoring_hr_data_mesgs"])
        rhr = rhr_df["resting_heart_rate"][0]  # current_day_resting_heart_rate

        return rhr
