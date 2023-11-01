import numpy as np
import pandas as pd
from garmin_fit_sdk import Decoder, Stream, Profile
import datetime

class Garmin:

    def __init__(self):
        self.messages = None
        self.raw_data = None
        self.stress = None
        self.SpO2 = None
        self.floor = None
        self.hr = None
        self.distance = None
        self.intensity = None
        self.calories = None
        self.sleep_time = None
        self.wake_time = None
        self.rhr = None

    def convert_time(df):
        df['timestamp'] = [datetime.datetime.utcfromtimestamp(631065600 + df['timestamp'][i]) - datetime.timedelta(hours=4)
                                        for i in range(len(df['timestamp']))]
        return df
    
    def get_timestamp(df):
        for i in range(len(df)-1):
            if df.iloc[i,0].astype(str) == 'nan':
                timestamp_16 = df['timestamp_16'][i]
                df.iloc[i,0] = df.iloc[(i-1),0]

        for i in range(len(df)):
            mesgTimestamp = int(df['timestamp'][i])
            try: 
                timestamp_16 = int(df['timestamp_16'][i])
                duration = ( timestamp_16 - ( mesgTimestamp & 0xFFFF ) ) & 0xFFFF
            except ValueError:
                continue
            mesgTimestamp += duration
            df.iloc[i,0] = mesgTimestamp
        return df

    @classmethod
    def read_fit(cls, path):
        """
        Reads FIT file and stores the data in the class instance.

        Args:
            file (str): The path to the FIT file to be read.
        """
        stream = Stream.from_file(path)
        decoder = Decoder(stream)
        messages, errors = decoder.read(apply_scale_and_offset=True,
                                        convert_datetimes_to_dates=False,
                                        convert_types_to_strings=True,
                                        enable_crc_check=True,
                                        expand_sub_fields=True,
                                        expand_components=True,
                                        merge_heart_rates=False,
                                        mesg_listener=None)
        
        cls.messages = messages
    
    @classmethod
    def get_raw_data(cls):
        raw_data = pd.DataFrame(cls.messages['monitoring_mesgs'])
        raw_data = cls.get_timestamp(raw_data)
        raw_data = cls.convert_time(raw_data)
        cls.raw_data = raw_data
    
    @classmethod
    def get_stress_level(cls):
        stress = pd.DataFrame(cls.messages['stress_level_mesgs'])
        stress['stress_level_time'] = [datetime.datetime.utcfromtimestamp(631065600 + stress['stress_level_time'][i]) - datetime.timedelta(hours=4)
                                        for i in range(len(stress['stress_level_time']))]
        cls.stress = stress
    
    @classmethod
    def get_SpO2(cls):
        SpO2 = pd.DataFrame(cls.messages['spo2_data_mesgs'])
        SpO2 = cls.convert_time(SpO2)
        cls.SpO2 = SpO2
    
    @classmethod
    def get_floor(cls):
        floor = cls.raw_data[['timestamp', 'ascent', 'descent']]
        floor.iloc[0,1:] = 0
        for i in range(len(floor)-1):
            if str(floor['ascent'][i+1]) == 'nan':
                floor.iloc[i+1,1] = floor.iloc[i,1]
            else:
                floor.iloc[i+1,1] += floor.iloc[i,1]

            
            if str(floor['descent'][i+1]) == 'nan':
                floor.iloc[i+1,2] = floor.iloc[i,2]
            else:
                floor.iloc[i+1,2] += floor.iloc[i,2]

        cls.floor = floor
    
    @classmethod
    def get_distance(cls):
        distance = cls.raw_data.iloc[:-5,:]
        distance = distance[['timestamp', 'distance']]
        distance.iloc[0,1] = 0
        for i in range(len(distance)-1):
            i = i + 1
            if str(distance['distance'][i]) == 'nan':
                if str(distance['distance'][i-1]) != 'nan':
                    distance.iloc[i,1] = distance['distance'][i-1]
            
            if distance.iloc[i,1] < distance['distance'][i-1]:
                distance.iloc[i,1] = distance['distance'][i-1]

        cls.distance = distance

    @classmethod
    def get_hr(cls):
        hr_df = cls.raw_data[~cls.raw_data['heart_rate'].isna()].reset_index(drop=True)
        hr_df = hr_df[['timestamp', 'heart_rate']]
        cls.hr = hr_df

    @classmethod
    def get_intensity(cls):
        intensity = cls.raw_data[~cls.raw_data['intensity'].isna()].reset_index(drop=True)
        intensity = intensity[['timestamp', 'intensity']]
        cls.intensity = intensity

    @classmethod
    def get_calories(cls):
        calories = cls.raw_data.iloc[:-5,:]
        calories = calories[['timestamp', 'active_calories']]
        for i in range(len(calories)-1):
            if str(calories['active_calories'][i+1]) == 'nan' or calories['active_calories'][i+1] < calories['active_calories'][i]:
                calories.iloc[i+1,1] = calories.iloc[i,1]
        cls.calories = calories
    
    @classmethod
    def get_sleep_time(cls):
        sleep = pd.DataFrame(cls.messages['sleep_level_mesgs'])
        sleep = cls.convert_time(sleep)
        for i in range(len(sleep['timestamp']) - 1):
            time_difference = sleep['timestamp'][i + 1] - sleep['timestamp'][i]
            if time_difference.seconds // 3600 > 1:
                sleep_time = sleep['timestamp'][i]
                wake_time = sleep['timestamp'][i + 1]
        
        cls.sleep_time = sleep_time
        cls.wake_time = wake_time
    
    @classmethod
    def get_rhr(cls):
        rhr_df = pd.DataFrame(cls.messages['monitoring_hr_data_mesgs'])
        rhr = rhr_df['resting_heart_rate'][0] # current_day_resting_heart_rate

        cls.rhr = rhr
