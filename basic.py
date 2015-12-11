import pandas as pd

# FIXME: date format in output file (1 day offset)
# FIXME: 'CAL yyyy' date format
# FIXME: compute min and max presence (date)
# FIXME: datetime unit in days instead of ns

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
for family_id, children_ids in couples['Children'].iteritems():
    if not pd.isnull(children_ids):
        children = individus.loc[map(int, str(children_ids).split(';')), 'BIRT_DATE']
        children = children.sort_values()
        children.index = ['BIRT_DATE_CHILD_%d' % i for i in range(1, len(children.index) + 1)]
        mother_id = couples.loc[family_id, 'MotherId']
        for column, birth_date in children.iteritems():
            if column not in final:
                final[column] = None
            final.loc[mother_id, column] = birth_date


final.to_excel('final.xls')
