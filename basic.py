from datetime import datetime
import pandas as pd
import numpy as np
from utils import read_source


# returns the best possible union date
def get_union_date(marriage):
    marr = marriage['MARR_DATE']
    if not pd.isnull(marr):
        return marr

    # civil union
    mare = marriage['EVEN_DATE']
    if not pd.isnull(mare):
        return mare

    marb = marriage['MARB_DATE']
    if not pd.isnull(marb):
        return marb + pd.Timedelta(days=21)

    return np.nan


def get_children_birthday(marriage):
    children_ids = marriage['Children']
    if not pd.isnull(children_ids):
        children = individus.loc[map(int, str(children_ids).split(';')), 'BIRT_DATE']
        return children.sort_values()
    return pd.Series()


def get_partner_id(person_id, marriage):
    if marriage['MotherId'] == person_id:
        return marriage['FatherId']
    elif marriage['FatherId'] == person_id:
        return marriage['MotherId']
    else:
        raise AssertionError


def format_date(date):
    # http://blog.sneawo.com/blog/2015/04/08/strftime-for-datetime-before-1900-year/
    # date.strftime('%d/%m/%Y')
    if not pd.isnull(date):
        return '{0.day:02d}/{0.month:02d}/{0.year}'.format(date)

individus, couples = read_source()

# remove marriages with unknown mother or father
couples = couples[(couples.MotherId != 0) & (couples.FatherId != 0)]

final = individus.copy()

age_in_days = final.DEAT_DATE - final.ESTIM_BIRT_DATE
final['AGE_AT_DEATH'] = (age_in_days[age_in_days.notnull()].dt.days / 365).astype(int)

# mothers and fathers marriages
for gender_groups in [couples.groupby('MotherId'), couples.groupby('FatherId')]:
    for person_id, group in gender_groups:
        sorted_group = group.sort_values(['MARR_DATE', 'EVEN_DATE', 'MARB_DATE'])
        birth_date = final.loc[person_id, 'ESTIM_BIRT_DATE']
        for index, (_, marriage) in enumerate(sorted_group.iterrows(), 1):
            columns = [('MARB_DATE', 'MARB_DATE_%d' % index),
                       ('MARR_DATE', 'MARR_DATE_%d' % index)]
            for column, final_name in columns:
                if final_name not in final:
                    final[final_name] = ''
                final.at[person_id, final_name] = format_date(marriage[column])

            # column = 'MARR_ID_%d' % index
            # if column not in final:
            #     final[column] = ''
            # final.at[person_id, column] = marriage.index

            # column = 'MARR_TYPE_%d' % index
            # if column not in final:
            #     final[column] = ''
            # final.at[person_id, column] = marriage['_UST']

            union_date = get_union_date(marriage)
            column = 'MARR_CALC_%d' % index
            if column not in final:
                final[column] = ''
            final.at[person_id, column] = format_date(union_date)

            column = 'MARR_DATE_OK_%d' % index
            if column not in final:
                final[column] = ''
            if not pd.isnull(union_date):
                final.at[person_id, column] = union_date > datetime(1790, 1, 1) and union_date < datetime(1850, 1, 1)

            column = 'AGE_MARR_%d' % index
            if column not in final:
                final[column] = np.nan
            if not pd.isnull(union_date) and not pd.isnull(birth_date):
                final.at[person_id, column] = (union_date - birth_date).days / 365

            children_birthday = get_children_birthday(marriage)
            children_birthday_diff = children_birthday.diff()
            first_child_index = children_birthday.first_valid_index()
            last_child_index = children_birthday.last_valid_index()
            last_child_birth_date = np.nan
            if not pd.isnull(last_child_index):
                last_child_birth_date = children_birthday[last_child_index]

            column = 'CHILD_COUNT_%d' % index
            if column not in final:
                final[column] = np.nan
            final.at[person_id, column] = len(children_birthday)

            column = 'DIFF_CHILD_%d' % index
            if column not in final:
                final[column] = ''
            final.at[person_id, column] = ' '.join([str(d.days) for d in children_birthday_diff if not pd.isnull(d)])

            column = 'MEAN_DIFF_CHILD_%d' % index
            if column not in final:
                final[column] = np.nan
            children_birthday_diff_mean = children_birthday_diff.mean()
            if not pd.isnull(children_birthday_diff_mean):
                final.at[person_id, column] = children_birthday_diff_mean.days

            column = 'DAYS_BEFORE_FIRST_CHILD_%d' % index
            if column not in final:
                final[column] = np.nan
            if not pd.isnull(union_date) and not pd.isnull(first_child_index):
                final.at[person_id, column] = (children_birthday.loc[first_child_index] - union_date).days

            column = 'LAST_CHILD_DATE_OK_%d' % index
            if column not in final:
                final[column] = ''
            if not pd.isnull(last_child_birth_date):
                final.at[person_id, column] = last_child_birth_date < datetime(1850, 1, 1)

            column = 'AGE_AT_LAST_CHILD_%d' % index
            if column not in final:
                final[column] = np.nan
            if not pd.isnull(last_child_birth_date) and not pd.isnull(birth_date):
                # we have at least one birth date
                person_age_at_last_child = last_child_birth_date - birth_date
                if not pd.isnull(person_age_at_last_child):
                    final.loc[person_id, column] = person_age_at_last_child.days / 365

            column = 'POSSIBLE_CPT_BY_STOPING_%d' % index
            if column not in final:
                final[column] = ''
            if not pd.isnull(last_child_birth_date):
                death_date = final.loc[person_id, 'DEAT_DATE']
                partner_death_date = final.loc[get_partner_id(person_id, marriage), 'DEAT_DATE']
                if not pd.isnull(death_date) and not pd.isnull(partner_death_date):
                    lives_enough_after = (death_date - last_child_birth_date).days > 900
                    partner_lives_enough_after = (partner_death_date - last_child_birth_date).days > 900
                    final.loc[person_id, column] = lives_enough_after and partner_lives_enough_after

            column = 'CHILDREN_BIRTHDAY_%d' % index
            if column not in final:
                final[column] = ''
            final.at[person_id, column] = ' '.join([format_date(d) for d in children_birthday if not pd.isnull(d)])


# FIXME: discover columns type
for col in ['BIRT_DATE', 'ESTIM_BIRT_DATE', 'CHR_DATE', 'DEAT_DATE']:
    final[col] = final[col].apply(format_date)

writer = pd.ExcelWriter('final.xls')
final.to_excel(writer, sheet_name='Individuals')

writer.save()
writer.close()
