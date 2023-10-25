import pandas
from garmin_fit_sdk import Decoder, Stream
import datetime


class GarminDataProcessor:
    FIT_EPOCH_S = 631065600

    def __init__(self):
        self.data = None

    def read_fit(self, file):
        """
        Reads FIT file and stores the data in the class instance.

        Args:
            file (str): The path to the FIT file to be read.
        """
        stream = Stream.from_file(file)
        decoder = Decoder(stream)
        messages, errors = decoder.read(
            apply_scale_and_offset=True,
            convert_datetimes_to_dates=False,
            convert_types_to_strings=True,
            enable_crc_check=True,
            expand_sub_fields=True,
            expand_components=True,
            merge_heart_rates=False,
            mesg_listener=None
        )
        print(errors)
        self.data = messages

    def convert_time(self):
        """
        Converts timestamps in the stored data to a human-readable format.

        Uses the FIT_EPOCH_S constant and adjusts for the time zone.

        Note: Requires data to be loaded using `read_fit` method first.
        """
        time_delta = datetime.timedelta(hours=4)
        if self.data is None:
            return None
        self.data['timestamp'] = [
            datetime.datetime.utcfromtimestamp(
                self.FIT_EPOCH_S + self.data['timestamp'][i]) - time_delta
            for i in range(len(self.data['timestamp']))
        ]

    def get_sleep_time(self):
        """
        Extracts sleep start and wake times from the stored data.

        Note: Requires data to be loaded and timestamps to be converted using
        `read_fit` and `convert_time` methods.
        """
        if self.data is None:
            return None
        sleep = self.data  # Replace with the actual sleep data frame
        sleep_time, wake_time = None, None
        for i in range(len(sleep['timestamp']) - 1):
            time_difference = sleep['timestamp'][i + 1] - sleep['timestamp'][i]
            if time_difference.seconds // 3600 > 1:
                sleep_time = sleep['timestamp'][i]
                wake_time = sleep['timestamp'][i + 1]
        return sleep_time, wake_time

    def get_timestamp(self):
        """
        Adjusts timestamps in the stored data, fixing inconsistencies and
        converting them to a continuous sequence.

        Note: Requires data to be loaded using `read_fit` method first.
        """
        if self.data is None:
            return None
        df = self.data  # Replace with the actual data frame
        for i in range(len(df) - 1):
            if df.iloc[i, 0].astype(str) == 'nan':
                timestamp_16 = df['timestamp_16'][i]
                df.iloc[i, 0] = df.iloc[(i - 1), 0]

        for i in range(len(df)):
            mesgTimestamp = int(df['timestamp'][i])
            try:
                timestamp_16 = int(df['timestamp_16'][i])
                duration = (timestamp_16 - (mesgTimestamp & 0xFFFF)) & 0xFFFF
            except ValueError:
                continue
            mesgTimestamp += duration
            df.iloc[i, 0] = mesgTimestamp

    def get_floor(self):
        """
        Calculates cumulative ascent and descent values over time,
        returning a data frame.

        Note: Requires data to be loaded using `read_fit` method first.
        """
        if self.data is None:
            return None
        df = self.data  # Replace with the actual data frame
        floor = df[['timestamp', 'ascent', 'descent']]
        floor.iloc[0, 1:] = 0
        for i in range(len(floor) - 1):
            if str(floor['ascent'][i + 1]) == 'nan':
                floor.iloc[i + 1, 1] = floor.iloc[i, 1]
            else:
                floor.iloc[i + 1, 1] += floor.iloc[i, 1]

            if str(floor['descent'][i + 1]) == 'nan':
                floor.iloc[i + 1, 2] = floor.iloc[i, 2]
            else:
                floor.iloc[i + 1, 2] += floor.iloc[i, 2]
        return floor

    def get_distance(self):
        """
        Calculates cumulative distance values over time,
        returning a data frame.

        Note: Requires data to be loaded using `read_fit` method first.
        """
        if self.data is None:
            return None
        df = self.data  # Replace with the actual data frame
        distance = df.iloc[:-5, :]
        distance = distance[['timestamp', 'distance']]
        distance.iloc[0, 1] = 0
        for i in range(len(distance) - 1):
            i = i + 1
            if str(distance['distance'][i]) == 'nan':
                if str(distance['distance'][i - 1]) != 'nan':
                    distance.iloc[i, 1] = distance['distance'][i - 1]

            if distance.iloc[i, 1] < distance['distance'][i - 1]:
                distance.iloc[i, 1] = distance['distance'][i - 1]
        return distance

    def get_hr(self):
        """
        Extracts heart rate data from the stored data.

        Note: Requires data to be loaded using `read_fit` method first.
        """
        if self.data is None:
            return None
        hr_df = self.data[~self.data['heart_rate'].isna()]
        hr_df = hr_df.reset_index(drop=True)
        hr_df = hr_df[['timestamp', 'heart_rate']]
        return hr_df

    def get_intensity(self):
        """
        Extracts intensity data from the stored data.

        Note: Requires data to be loaded using `read_fit` method first.
        """
        if self.data is None:
            return None
        intensity = self.data[~self.data['intensity'].isna()]
        intensity = intensity.reset_index(drop=True)
        intensity = intensity[['timestamp', 'intensity']]
        return intensity

    def get_calories(self):
        """
        Calculates cumulative active calorie values over time,
        returning a data frame.

        Note: Requires data to be loaded using `read_fit` method first.
        """
        if self.data is None:
            return None
        calories = self.data.iloc[:-5, :]
        calories = calories[['timestamp', 'active_calories']]
        for i in range(len(calories) - 1):
            if str((calories['active_calories'][i + 1]) == 'nan') or\
                (calories['active_calories'][i + 1] <
                 calories['active_calories'][i]):
                calories.iloc[i + 1, 1] = calories.iloc[i, 1]
        return calories
