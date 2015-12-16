import datetime
import pandas as pd
import ggplot as gg
import matplotlib.pyplot as plt
import seaborn as sbn
from scipy.stats import probplot
from utils import read_source

individus, couples = read_source()

family_children = couples[['MARB_DATE', 'MARR_DATE']].copy()

# remove families without dates
no_marb = pd.isnull(family_children.MARB_DATE)
no_marr = pd.isnull(family_children.MARR_DATE)
family_children = family_children[~no_marb | ~no_marr]

# family_children['MARB_DATE'] - family_children['MARR_DATE']

# if the marriage date is unknown, the estimated date is banns + 21 days
family_children.loc[no_marr, 'MARR_DATE'] = family_children.MARB_DATE + pd.Timedelta(days=21)

family_children['FIRST_CHILD'] = pd.NaT
family_children['CHILD_NAME'] = ''
# first children birth
for family_id, children_ids in couples['Children'].iteritems():
    if not pd.isnull(children_ids) and family_id in family_children.index:
        children = individus.loc[map(int, str(children_ids).split(';')), ['BIRT_DATE', 'Name']]
        children = children[~children.BIRT_DATE.isnull()]
        if len(children) > 0:
            children = children.sort_values('BIRT_DATE')
            first_child = children.iloc[0]
            family_children.loc[family_id, 'FIRST_CHILD'] = first_child['BIRT_DATE']
            family_children.loc[family_id, 'CHILD_NAME'] = first_child['Name']

# remove families without valid 'FIRST_CHILD'
family_children = family_children[~pd.isnull(family_children.FIRST_CHILD)]

# compute number of days between birth of the first child and the marriage date
family_children['DIFF'] = (family_children['FIRST_CHILD'] - family_children['MARR_DATE']).dt.days

# FIXME: simplify
final = family_children[family_children.columns]
final = final.set_index('FIRST_CHILD')
final = final.sort_index()

#final = final[final.DIFF < 1095]

nine_months = 274

q10 = pd.rolling_quantile(final['DIFF'], 40, 0.1)
q50 = pd.rolling_quantile(final['DIFF'], 40, 0.5)
q90 = pd.rolling_quantile(final['DIFF'], 40, 0.9)

above = final[final.DIFF > nine_months]
bellow = final[final.DIFF <= nine_months]

jomini = final[final.CHILD_NAME.str.contains('JOMINI')]

# %matplotlib inline
sbn.set_style('ticks')

plt.figure()
# plt.plot(above.index, above.DIFF, marker='o', color='0.75', linestyle='')
# plt.plot(bellow.index, bellow.DIFF, marker='o', color='0.5',linestyle='')
plt.plot(final.index, final.DIFF, marker='o', color='black', alpha=0.1, linestyle='')
#plt.plot(jomini.index, jomini.DIFF, marker='s', color='red', linestyle='')
plt.axhline(0, linewidth=0.5, color='black', linestyle='dotted')
plt.axhline(nine_months, linewidth=0.5, color='black', linestyle='dotted')
#plt.fill_between(final.index, 0, nine_months, color='0.6', alpha=0.2)
#plt.fill_between(final.index, q10, q90, color='0.3', alpha=0.2)
plt.plot(final.index, q50, linewidth=1, alpha=0.5)
plt.xlim(plt.xlim(datetime.date(1790, 1, 1), datetime.date(1855, 1, 1)))
plt.ylim(-500, 1500)

plt.ylabel('jours')

ylocs, _ = plt.yticks()
plt.yticks(sorted(list(ylocs) + [nine_months]))

sbn.despine()


sbn.distplot(final.DIFF, rug=True)
probplot(final.DIFF, plot=plt)

sbn.kdeplot(final.index.year, final.DIFF)
plt.xlim(1790, 1855)
plt.ylim(-1000, 2000)
