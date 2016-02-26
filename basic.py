import pandas as pd
import numpy as np
from utils import read_source

# FIXME: fix date in output xls (convert to string)
# FIXME: 'CAL yyyy' date format
# FIXME: compute min and max presence (date)
# FIXME: datetime unit in days instead of ns


def get_union_date(marriage):
    marr = marriage['MARR_DATE']
    if pd.isnull(marr):
        marb = marriage['MARB_DATE']
        if not pd.isnull(marb):
            return marb + pd.Timedelta(days=21)
    else:
        return marr
    return np.nan


def get_children_birthday(marriage):
    children_ids = marriage['Children']
    if not pd.isnull(children_ids):
        children = individus.loc[map(int, str(children_ids).split(';')), 'BIRT_DATE']
        return children.sort_values()
    return pd.Series()

individus, couples = read_source()

# remove marriage with unknown mother or father
couples = couples[(couples.MotherId != 0) & (couples.FatherId != 0)]

final = individus[['Name', 'Gender', 'BIRT_DATE', 'CHR_DATE', 'DEAT_DATE']].copy()

# mothers and fathers marriages
for gender_groups in [couples.groupby('MotherId'), couples.groupby('FatherId')]:
    for person_id, group in gender_groups:
        sorted_group = group.sort_values(['MARB_DATE', 'MARR_DATE'])
        for index, (_, marriage) in enumerate(sorted_group.iterrows(), 1):
            columns = [('MARB_DATE', 'MARB_DATE_%d' % index),
                       ('MARR_DATE', 'MARR_DATE_%d' % index)]
            for column, final_name in columns:
                if final_name not in final:
                    final[final_name] = pd.NaT
                final.at[person_id, final_name] = marriage[column]

            union_date = get_union_date(marriage)
            column = 'MARR_CALC_%d' % index
            if column not in final:
                final[column] = pd.NaT
            final.at[person_id, column] = union_date

            column = 'AGE_MARR_%d' % index
            if column not in final:
                final[column] = np.nan
            birth_date = final.loc[person_id, 'BIRT_DATE']
            if not pd.isnull(union_date) and not pd.isnull(birth_date):
                final.at[person_id, column] = (union_date - birth_date).days / 365

            column = 'DAYS_BEFORE_FIRST_CHILD_%d' % index
            children_birthday = get_children_birthday(marriage)
            first_child_index = children_birthday.first_valid_index()
            if column not in final:
                final[column] = np.nan
            if not pd.isnull(union_date) and not pd.isnull(first_child_index):
                final.at[person_id, column] = (children_birthday.loc[first_child_index] - union_date).days


final['CHILD_COUNT'] = np.nan
final['AGE_AT_LAST_CHILD'] = np.nan
final['DIFF_CHILD'] = ''
final['MEAN_DIFF_CHILD'] = np.nan
# children births
for family_id, children_ids in couples['Children'].iteritems():
    mother_id = couples.loc[family_id, 'MotherId']
    father_id = couples.loc[family_id, 'FatherId']
    if not pd.isnull(children_ids):
        children = individus.loc[map(int, str(children_ids).split(';')), 'BIRT_DATE']
        children = children.sort_values()
        children.index = ['BIRT_DATE_CHILD_%d' % i for i in range(1, len(children.index) + 1)]
        last_child_birth_date_index = children.last_valid_index()
        if not pd.isnull(last_child_birth_date_index):
            # we have at least one birth date
            last_child_birth_date = children[last_child_birth_date_index]
            for person_id in [mother_id, father_id]:
                # FIXME: test if the person lives after this birth
                person_age_at_last_child = last_child_birth_date - final.loc[person_id, 'BIRT_DATE']
                if not pd.isnull(person_age_at_last_child):
                    final.loc[person_id, 'AGE_AT_LAST_CHILD'] = person_age_at_last_child.days / 365

        final.loc[mother_id, 'CHILD_COUNT'] = len(children)
        for column, birth_date in children.iteritems():
            if column not in final:
                final[column] = pd.NaT
            final.loc[mother_id, column] = birth_date

        final.loc[mother_id, 'DIFF_CHILD'] = ','.join([str(d.days) for d in children.diff() if not pd.isnull(d)])
        # mean time between births
        mean_diff_child = children.diff().mean()
        if not pd.isnull(mean_diff_child):
            final.loc[mother_id, 'MEAN_DIFF_CHILD'] = mean_diff_child.days
    else:
        final.loc[mother_id, 'CHILD_COUNT'] = 0

writer = pd.ExcelWriter('final.xls',  datetime_format='DD/MM/YYYY')
final.to_excel(writer)
writer.close()
