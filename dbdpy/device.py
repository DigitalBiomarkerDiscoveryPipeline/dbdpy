class CommercialDevice:
    def __init__(self, brand, model=None):
        self.brand = brand
        self.model = model

    def get_device_info(self):
        """Retrieve brand and model name of a device.

        Paramters
        ---------
        None

        Returns
        -------
        device_info : str
        """
        device_info = f"{self.brand} - {self.model}"
        return device_info

    def heart_rate(self):
        '''Get heart_rate dataframe 
        
        Returns
        -------
        heart_rate: pandas.DataFrame
            Dataframe with columns for timestamp (datetime64) and heart_rate in bpm (int)
        '''
        return self._heart_rate()
    
    def active_calories(self):
        '''Get active_calories dataframe 
        
        Returns
        -------
        active_calories: pandas.DataFrame
            Dataframe with columns for start_time (datetime64), end_time (datetime64) and active calories in kilocalories (int)
        '''
        return self._active_calories()
    
    def distance(self):
        '''Get distance dataframe 
        
        Returns
        -------
        distance: pandas.DataFrame
            Dataframe with columns for start_time (datetime64), end_time (datetime64) and distance in meters (int)
        '''
        return self._distance()
    
    def spo2(self):
        '''Get SpO2 dataframe 
        
        Returns
        -------
        spo2: pandas.DataFrame
            Dataframe with columns for timestamp (datetime64) and SpO2 % (int)
        '''
        return self._spo2()
    
    def steps(self):
        '''Get steps dataframe 
        
        Returns
        -------
        steps: pandas.DataFrame
            Dataframe with columns for start_time (datetime64), end_time (datetime64) and step count (int)
        '''
        return self._steps()
    
    def sleep_stage_summary(self):
        '''Get summary of sleep stages for the night of a day
        
        Returns
        -------
        sleep_stage_summary: pandas.DataFrame
            Dataframe with columns for date (datetime64), wake (seconds, int), light (seconds, int), deep (seconds, itn), REM (seconds, int) '''
        return self._sleep_stage_summary()