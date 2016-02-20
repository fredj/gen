import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sbn
from utils import read_source


individus_columns = {
    'BIRT_DATE': 'FIRST_CHILD',
    'Name': 'CHILD_NAME',
    'no lign pat': 'FATHER_LINE',
    'no lign mat': 'MOTHER_LINE',
}

individus, couples = read_source()

family_children = couples[['MARB_DATE', 'MARR_DATE']].copy()

# remove families without dates
family_children = family_children[~family_children.MARB_DATE.isnull() | ~family_children.MARR_DATE.isnull()]

# if the marriage date is unknown, the estimated date is banns + 21 days
family_children.loc[family_children.MARR_DATE.isnull(), 'MARR_DATE'] = family_children.MARB_DATE + pd.Timedelta(days=21)


# first children birth
for family_id, children_ids in couples['Children'].iteritems():
    if not pd.isnull(children_ids) and family_id in family_children.index:
        children = individus.loc[map(int, str(children_ids).split(';')), individus_columns.keys()]
        children = children[~children.BIRT_DATE.isnull()]
        if len(children) > 0:
            children = children.sort_values('BIRT_DATE')
            first_child = children.iloc[0]
            # copy values from 'individus'
            for k,v in individus_columns.iteritems():
                family_children.loc[family_id, v] = first_child[k]

# remove families without valid 'FIRST_CHILD'
family_children = family_children[~family_children.FIRST_CHILD.isnull()]

# compute number of days between birth of the first child and the marriage date
family_children['DIFF'] = (family_children['FIRST_CHILD'] - family_children['MARR_DATE']).dt.days

# from 1790 to 1856
# family_children = family_children[family_children.MARR_DATE > datetime.date(1790, 1, 1)]
# family_children = family_children[family_children.MARR_DATE < datetime.date(1856, 1, 1)]

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

#final.groupby('FATHER_LINE').size().sort_values()
group = final[final.FATHER_LINE == 73863]

# %matplotlib inline
sbn.set_style('ticks')

plt.figure()
# plt.plot(above.index, above.DIFF, marker='o', color='0.75', linestyle='')
# plt.plot(bellow.index, bellow.DIFF, marker='o', color='0.5',linestyle='')
plt.plot(final.index, final.DIFF, marker='o', color='black', alpha=0.1, linestyle='')
plt.plot(group.index, group.DIFF, marker='s', color='red', linestyle='')
plt.axhline(0, linewidth=0.75, color='black', linestyle='dotted')
plt.axhline(nine_months, linewidth=0.5, color='black', linestyle='dotted')
#plt.fill_between(final.index, 0, nine_months, color='0.6', alpha=0.2)
#plt.fill_between(final.index, q10, q90, color='0.3', alpha=0.2)
#plt.plot(final.index, q50, linewidth=1, alpha=0.5)

plt.xlim(plt.xlim(datetime.date(1790, 1, 1), datetime.date(1855, 1, 1)))
plt.ylim(-500, 1500)

plt.ylabel('jours')

ylocs, _ = plt.yticks()
plt.yticks(sorted(list(ylocs) + [nine_months]))

sbn.despine()


sbn.distplot(final.DIFF, rug=True)

sbn.kdeplot(final.index.year, final.DIFF)
plt.xlim(1790, 1855)
plt.ylim(-1000, 2000)
