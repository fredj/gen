import pandas as pd

def read_source():
    individus = pd.read_excel('Payerne.xls', 'Individuals', index_col=0)
    couples = pd.read_excel('Payerne.xls', 'Families', index_col=0)

    # convert columns to datetime
    to_datetime(individus, ['BIRT_DATE', 'CHR_DATE', 'DEAT_DATE'])
    to_datetime(couples, ['MARB_DATE', 'MARR_DATE'])
    return individus, couples


def to_datetime(data_frame, columns):
    for column in columns:
        data_frame[column] = pd.to_datetime(data_frame[column], errors='coerce')
