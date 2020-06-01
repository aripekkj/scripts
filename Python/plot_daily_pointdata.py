# -*- coding: utf-8 -*-
"""
Created on Wed May 13 08:10:27 2020

@author: Ap
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import *
import datetime
import numpy as np

# filepaths
fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\fire_030405_2019_PAs_nh.shp'
fp2 = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\fire_030405_2020_PAs_nh.shp'


# set date time index range
idx19 = pd.date_range('2019-03-01', '2019-05-17')
idx20 = pd.date_range('2020-03-01', '2020-05-17')

# read file
fire19 = gpd.read_file(fp)
fire20 = gpd.read_file(fp2)


# empty column for cumulative sum
fire19['sum'] = 1

# group by date
test = fire19.groupby('ACQ_DATE')['sum'].sum()
test.index = pd.DatetimeIndex(test.index) # set index as datetimeindex

# reindex to date range and fill empty rows with 0
test = test.reindex(idx19, fill_value=0)

# convert Series to DataFrame and count cumulative sum to new column
df = pd.Series.to_frame(test)
df['cumsum'] = df['sum'].cumsum()


#
# same as above to 2020 data
# should update this to avoid repeating
#

# empty column for cumulative sum
fire20['sum'] = 1

# group by date
test20 = fire20.groupby('ACQ_DATE')['sum'].sum()
test20.index = pd.DatetimeIndex(test20.index) # set index as datetimeindex

# reindex to date range and fill empty rows with 0
test20 = test20.reindex(idx20, fill_value=0)

# convert Series to DataFrame and count cumulative sum to new column
df2 = pd.Series.to_frame(test20)
df2['cumsum'] = df2['sum'].cumsum()



# reset index
df19 = df.reset_index()
df20 = df2.reset_index()

# merge
merged = pd.merge(df19, df20, how='inner', left_index=True, right_index=True)

merged['datetime'] = pd.to_datetime(merged['index_x'])
merged['MM-DD'] = merged['datetime'].dt.strftime('%m-%d')

# Then make plot

# filepath for figure
fig_fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\viirs_fa_030405_1920_PAs_nh.png'

# plot
barwidth=0.25

r1 = np.arange(len(merged['MM-DD']))
r2 = [x + barwidth for x in r1]
r3 = [x + barwidth for x in r2]

plt.xticks(rotation='vertical', fontsize=5)
plt.bar(r2, merged['sum_x'], color='b', width=barwidth, label='2019')
plt.bar(r3, merged['sum_y'], color='r', width=barwidth, label='2020')
plt.xticks([r + barwidth for r in range(len(merged['MM-DD']))], merged['MM-DD'])
plt.title('FIRMS VIIRS data on Madagascar protected areas')
plt.ylabel('Number of active fires / thermal anomalies')
plt.xlabel('Date')
plt.legend(loc='upper left')
plt.text(len(r1),-10, 'right top', text='Digital Geography Lab / Ari-Pekka Jokinen', 
         horizontalalignment='right', fontsize=5)

plt.savefig(fig_fp, dpi=300, format='png')


"""
# try to plot with second y-axis
fig, ax = plt.subplots()

ax.bar(merged['MM-DD'], merged['sum_x'], width=0.3, color='blue', align='center')
ax.bar(merged['MM-DD'], merged['sum_y'], width=0.3, color='red', align='center')
ax.tick_params(axis='x', labelsize=5, rotation=90)


"""















