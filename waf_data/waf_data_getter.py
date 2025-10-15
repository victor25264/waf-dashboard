import pandas as pd 
from  datetime import datetime 

HOUR_SECONDS = 3600

class WAFDataGetter:
    def __init__(self, data_location:str, secret:str, http_client):
        self.data_location = data_location
        self.secret = secret
        self.http_client = http_client

    def __get_waf_data(self, start_time:float, end_time:float):
        response = self.http_client.get(self.data_location, headers={"Authorization": f"Bearer {self.secret}"}, params={"start": start_time, "end": end_time})
        if response.status_code == 200:
            response = response.json()
            return response["data"]
        else:
            response.raise_for_status()

    def get_waf_data(self, start_time:float=None, end_time:float=None):
        if start_time is None:
            start_time = (datetime.now().timestamp() - HOUR_SECONDS) 
        if end_time is None:
            end_time = datetime.now().timestamp()
        
        raw_data = self.__get_waf_data(start_time, end_time)
        waf_entries = pd.DataFrame.from_dict(raw_data)
        return waf_entries