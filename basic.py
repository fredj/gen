import pandas as pd

# FIXME: date format in output file (1 day offset)
# FIXME: 'CAL yyyy' date format
# FIXME: order children births by date

def to_datetime(data_frame, columns):
    for column in columns:
        data_frame[column] = pd.to_datetime(data_frame[column], errors='coerce')

individus = pd.read_excel('Payerne.xls', 'Individuals', index_col=0)
couples = pd.read_excel('Payerne.xls', 'Families', index_col=0)
# convert columns to datetime
to_datetime(individus, ['BIRT_DATE', 'CHR_DATE', 'DEAT_DATE'])
to_datetime(couples, ['MARB_DATE', 'MARR_DATE'])

# remove marriage with unknown mother or father
couples = couples[(couples.MotherId != 0) & (couples.FatherId != 0)]

final = individus[['Name', 'Gender', 'BIRT_DATE', 'CHR_DATE', 'DEAT_DATE']].copy()

# mothers marriages
for mother_id, group in couples.groupby('MotherId'):
    sorted_group = group.sort_values(['MARB_DATE', 'MARR_DATE'])
    for index, (_, marriages) in enumerate(sorted_group.iterrows(), 1):
        columns = [('MARB_DATE', 'MARB_DATE_%d' % index),
                   ('MARR_DATE', 'MARR_DATE_%d' % index)]
        for column, final_name in columns:
            if final_name not in final:
                final[final_name] = None
            final.at[mother_id, final_name] = marriages[column]

# fathers marriages
for father_id, group in couples.groupby('FatherId'):
    sorted_group = group.sort_values(['MARB_DATE', 'MARR_DATE'])
    for index, (_, marriages) in enumerate(sorted_group.iterrows(), 1):
        columns = [('MARB_DATE', 'MARB_DATE_%d' % index),
                   ('MARR_DATE', 'MARR_DATE_%d' % index)]
        for column, final_name in columns:
            if final_name not in final:
                final[final_name] = None
            final.at[father_id, final_name] = marriages[column]

# children births
for family_id, children in couples['Children'].iteritems():
    if not pd.isnull(children):
        mother_id = couples.ix[family_id, 'MotherId']
        for index, child in enumerate(str(children).split(';'), 1):
            columns = [('BIRT_DATE', 'BIRT_DATE_CHILD_%d' % index),
                       ('_FIL', 'FIL_CHILD_%d' % index)]
            for column, final_name in columns:
                if final_name not in final:
                    final[final_name] = None
                final.at[mother_id, final_name] = individus.ix[int(child), column]


# FIXME: compute min/max presence date

final.to_excel('final.xls')
