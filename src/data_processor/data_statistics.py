import pandas as pd

class DataStatistics:
    @staticmethod
    def count_by_column(data: pd.DataFrame, column_name: str):
        if column_name in data.columns:
            return data[column_name].value_counts().to_dict()
        else:
            raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
    
