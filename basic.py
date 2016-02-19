import pandas as pd
import numpy as np
from utils import read_source

# FIXME: fix date in output xls (convert to string)
# FIXME: 'CAL yyyy' date format
# FIXME: compute min and max presence (date)
# FIXME: datetime unit in days instead of ns

individus, couples = read_source()

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
                final[final_name] = pd.NaT
            final.at[mother_id, final_name] = marriages[column]

# fathers marriages
for father_id, group in couples.groupby('FatherId'):
    sorted_group = group.sort_values(['MARB_DATE', 'MARR_DATE'])
    for index, (_, marriages) in enumerate(sorted_group.iterrows(), 1):
        columns = [('MARB_DATE', 'MARB_DATE_%d' % index),
                   ('MARR_DATE', 'MARR_DATE_%d' % index)]
        for column, final_name in columns:
            if final_name not in final:
                final[final_name] = pd.NaT
            final.at[father_id, final_name] = marriages[column]

final['CHILD_COUNT'] = np.nan
final['AGE_AT_LAST_CHILD'] = np.nan
# children births
for family_id, children_ids in couples['Children'].iteritems():
    mother_id = couples.loc[family_id, 'MotherId']
    father_id = couples.loc[family_id, 'FatherId']
    if not pd.isnull(children_ids):
        children = individus.loc[map(int, str(children_ids).split(';')), 'BIRT_DATE']
        children = children.sort_values()
        children.index = ['BIRT_DATE_CHILD_%d' % i for i in range(1, len(children.index) + 1)]
        last_child_bith_date_index = children.last_valid_index()
        if not pd.isnull(last_child_bith_date_index):
            # we have at least one bith date
            last_child_bith_date = children[last_child_bith_date_index]
            # FIXME: test if the mother lives after this birth
            mother_age_at_last_child = last_child_bith_date - final.loc[mother_id, 'BIRT_DATE']
            if not pd.isnull(mother_age_at_last_child):
                final.loc[mother_id, 'AGE_AT_LAST_CHILD'] = mother_age_at_last_child.days / 365

            # FIXME: test if the father lives after this birth
            father_age_at_last_child = last_child_bith_date - final.loc[father_id, 'BIRT_DATE']
            if not pd.isnull(father_age_at_last_child):
                final.loc[father_id, 'AGE_AT_LAST_CHILD'] = father_age_at_last_child.days / 365

        # FIXME: compute mother's age at the last birth
        final.loc[mother_id, 'CHILD_COUNT'] = len(children)
        for column, birth_date in children.iteritems():
            if column not in final:
                final[column] = pd.NaT
            final.loc[mother_id, column] = birth_date
        # mean time between births
        mean_diff_child = children.diff().mean()
        if not pd.isnull(mean_diff_child):
            final.loc[mother_id, 'MEAN_DIFF_CHILD'] = mean_diff_child.days
    else:
        final.loc[mother_id, 'CHILD_COUNT'] = 0

writer = pd.ExcelWriter('final.xls',  datetime_format='DD/MM/YYYY')
final.to_excel(writer)
writer.close()
