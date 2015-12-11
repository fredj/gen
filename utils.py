import pandas as pd

def to_datetime(data_frame, columns):
    for column in columns:
        data_frame[column] = pd.to_datetime(data_frame[column], errors='coerce')
