import pandas as pd
import ggplot as gg
import matplotlib.pyplot as plt
from utils import to_datetime

individus = pd.read_excel('Payerne.xls', 'Individuals', index_col=0)
couples = pd.read_excel('Payerne.xls', 'Families', index_col=0)

to_datetime(individus, ['BIRT_DATE', 'CHR_DATE'])
to_datetime(couples, ['MARB_DATE', 'MARR_DATE'])

family_children = couples[['MARB_DATE', 'MARR_DATE']].copy()

# remove families without dates
no_marb = pd.isnull(family_children.MARB_DATE)
no_marr = pd.isnull(family_children.MARR_DATE)
family_children = family_children[~no_marb | ~no_marr]

# family_children['MARB_DATE'] - family_children['MARR_DATE']

# if the marriage date is unknown, the estimated date is banns + 21 days
family_children.loc[no_marr, 'MARR_DATE'] = family_children.MARB_DATE + pd.Timedelta(days=21)

family_children['FIRST_CHILD'] = pd.NaT
# first children birth
for family_id, children_ids in couples['Children'].iteritems():
    if not pd.isnull(children_ids) and family_id in family_children.index:
        children = individus.loc[map(int, str(children_ids).split(';')), 'BIRT_DATE']
        children = children.dropna()
        children = children.sort_values()
        if len(children) > 0:
            family_children.loc[family_id, 'FIRST_CHILD'] = children.iloc[0]

# remove families without valid 'FIRST_CHILD'
family_children = family_children[~pd.isnull(family_children.FIRST_CHILD)]

# compute number of days between birth of the first child and the marriage date
family_children['DIFF'] = (family_children['FIRST_CHILD'] - family_children['MARR_DATE']).dt.days

# FIXME: simplify
final = family_children[['FIRST_CHILD', 'DIFF']]
final = final.set_index('FIRST_CHILD')
final = final.sort_index()

q10 = pd.rolling_quantile(final['DIFF'], 40, 0.1)
q50 = pd.rolling_quantile(final['DIFF'], 40, 0.5)
q90 = pd.rolling_quantile(final['DIFF'], 40, 0.9)

above = final[final.DIFF > nine_months]
bellow = final[final.DIFF <= nine_months]

nine_months = 274

# %matplotlib inline

plt.figure()
# plt.plot(above.index, above.DIFF, marker='o', color='0.75', linestyle='')
# plt.plot(bellow.index, bellow.DIFF, marker='o', color='0.5',linestyle='')
plt.plot(final.index, final.DIFF, marker=',', color='0.75', linestyle='')
plt.fill_between(final.index, 0, nine_months, color='0.6', alpha=0.2)
plt.fill_between(final.index, q10, q90, color='0.3', alpha=0.2)
plt.plot(final.index, q50)
plt.ylim(-1000, 2000)
