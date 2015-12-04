import pandas as pd

individus = pd.read_excel('Payerne.xls', 'Individuals', index_col=0)
couples = pd.read_excel('Payerne.xls', 'Families', index_col=0)
# remove marriage with unknown mother
couples = couples[couples.MotherId != 0]

final = individus[['Name', 'Gender', 'BIRT_DATE', 'CHR_DATE', 'DEAT_DATE']].copy()

# individus[pd.notnull(individus.BIRT_DATE) & individus.BIRT_DATE.str.startswith('CAL')]

# FIXME: order by date
for mother_id, group in couples.groupby('MotherId'):
    for index, (_, marriages) in enumerate(group.iterrows(), 1):
        columns = [('MARB_DATE', 'MARB_DATE_%d' % index),
                   ('MARR_DATE', 'MARR_DATE_%d' % index)]
        for column, final_name in columns:
            if final_name not in final:
                final[final_name] = None
            final.at[mother_id, final_name] = marriages[column]


# FIXME: order by date
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
