import pandas as pd

def read_source():
    individus = pd.read_excel('Payerne.xls', 'Individuals', index_col=0)
    couples = pd.read_excel('Payerne.xls', 'Families', index_col=0)

    individus['ESTIM_BIRT_DATE'] = individus['BIRT_DATE']

    dayish = r'^(?:ABT|AFT|BEF|CAL) (\d{1,2} \w{3} \d{4})'
    estimated = individus.BIRT_DATE.str.extract(dayish)
    individus.loc[~estimated.isnull(), 'ESTIM_BIRT_DATE'] = estimated

    monthish = r'^(?:ABT|AFT|BEF|CAL)?\s?(\w{3} \d{4})'
    estimated = '1 ' + individus.BIRT_DATE.str.extract(monthish)
    individus.loc[~estimated.isnull(), 'ESTIM_BIRT_DATE'] = estimated

    yearish = r'^(?:ABT|AFT|BEF|CAL)?\s?(\d{4})'
    estimated = '1 JUL ' + individus.BIRT_DATE.str.extract(yearish)
    individus.loc[~estimated.isnull(), 'ESTIM_BIRT_DATE'] = estimated

    # convert columns to datetime
    to_datetime(individus, ['BIRT_DATE', 'ESTIM_BIRT_DATE', 'CHR_DATE', 'DEAT_DATE'])
    to_datetime(couples, ['MARB_DATE', 'MARR_DATE'])
    return individus, couples


def to_datetime(data_frame, columns):
    for column in columns:
        data_frame[column] = pd.to_datetime(data_frame[column], errors='coerce')
