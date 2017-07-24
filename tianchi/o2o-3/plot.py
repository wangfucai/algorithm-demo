# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

off_train = pd.read_csv('2016data/ccf_offline_stage1_train.csv', header=None)
off_train.columns = ['user_id', 'merchant_id', 'coupon_id', 'discount_rate', 'distance', 'date_received', 'date']

dataset = off_train
t1 = dataset[(dataset.date_received != 'null') & (dataset.date != 'null')][['date']]
t1['领券后消费数'] = 1
t1 = t1.groupby('date').agg('sum').reset_index()

t2 = dataset[(dataset.date_received == 'null') & (dataset.date != 'null')][['date']]
t2['没领券消费数'] = 1
t2 = t2.groupby('date').agg('sum').reset_index()

t3 = dataset[(dataset.date_received != 'null')][['date_received']]
t3['领券数'] = 1
t3 = t3.groupby('date_received').agg('sum').reset_index()


feature1 = pd.merge(t1, t2, on='date', how='left')
feature2 = pd.merge(t3, t1, left_on='date_received', right_on='date', how='left')
print feature2

font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=14)
df = pd.DataFrame(feature1, columns=['date', '领券后消费数', '没领券消费数'])
#ax = df.plot(x='date', secondary_y=['count1', 'count2'])
ax = df.plot(x='date')
#plt.legend(loc='upper center')
for label in ax.legend().texts:
    label.set_fontproperties(font)

plt.show(ax)

df1 = pd.DataFrame(feature2, columns=['date_received', '领券后消费数', '领券数'])
ax1 = df1.plot(x='date_received')
for label in ax1.legend().texts:
    label.set_fontproperties(font)
plt.show(ax1)
