# -*- coding: utf-8 -*-
"""
Created on Mon May 25 11:07:51 2020

@author: Ap
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May 13 08:10:27 2020

@author: Ap
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# filepaths
fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\fire_01032015_30062019_Madagascar_PAs.shp'
fp2 = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\fire_01032020_30062020_Madagascar_PAs.shp'
fp3 = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\WDPA\WDPA_Oct2019_Land_0_1manualClean.shp'

# set date time index range
idx19 = pd.date_range('2019-03-01', '2019-06-30')
idx20 = pd.date_range('2020-03-01', '2020-06-30')

# read file
fire19 = gpd.read_file(fp)
fire20 = gpd.read_file(fp2)
poly = gpd.read_file(fp3)

# filter low confidence points off
fire19 = fire19[fire19['CONFIDENCE'] != 'l']
fire20 = fire20[fire20['CONFIDENCE'] != 'l']

# filepath for figures
fig_fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\figures\Madagascar'

# function to count sum of fire records and group them by day
def groupByDate(df, dateindex):
    # empty column for cumulative sum
    df['sum'] = 1
    
    # group by date
    df_group = df.groupby('ACQ_DATE')['sum'].sum()
    df_group.index = pd.DatetimeIndex(df_group.index) # set index as datetimeindex
    
    # reindex to date range and fill empty rows with 0
    df_group = df_group.reindex(dateindex, fill_value=0)
    
    # convert Series to DataFrame and count cumulative sum to new column
    df_out = pd.Series.to_frame(df_group)
    df_out['cumsum'] = df_out['sum'].cumsum()
    
    return df_out;

# group whole data to find out max daily value
test19 = groupByDate(fire19, idx19)
test20 = groupByDate(fire20, idx20)

test19 = test19.reset_index()
test20 = test20.reset_index()

# merge
testmerged = pd.merge(test19, test20, how='inner', left_index=True, right_index=True)

testmerged['datetime'] = pd.to_datetime(testmerged['index_x'])
testmerged['MM-DD'] = testmerged['datetime'].dt.strftime('%m-%d')

maxval = max(testmerged['sum_x'])
if max(testmerged['sum_y']) > maxval:
    maxval = max(testmerged['sum_y'])

########################################
# Clip data by polygon and create plot #
########################################

# get a Series of protected area names
pas = poly['NAME']

# loop through protected areas
for i in pas:
    pa = poly[poly['NAME'] == i]
    
    # clip by protected area polygon
    pa_viirs19 = gpd.clip(fire19, pa)
    
    # group by date
    df19 = groupByDate(pa_viirs19, idx19)    

    # same to 2020 data
    # clip by protected area polygon
    pa_viirs20 = gpd.clip(fire20, pa)
    
    # group by date
    df20 = groupByDate(pa_viirs20, idx20)
    
    # reset index
    df19 = df19.reset_index()
    df20 = df20.reset_index()
    
    # merge
    merged = pd.merge(df19, df20, how='inner', left_index=True, right_index=True)
    
    merged['datetime'] = pd.to_datetime(merged['index_x'])
    merged['MM-DD'] = merged['datetime'].dt.strftime('%m-%d')
    
    # check if there is any fire records either year. If not, return to the beginning of the loop
    if (sum(merged['sum_x']) == 0) == True & (sum(merged['sum_y']) == 0) == True:
        print(i)
        continue
    
    # set bar width
    barwidth=0.25
    
    # some settings so the bars don't overlap
    r1 = np.arange(len(merged['MM-DD']))
    r2 = [x + barwidth for x in r1]
    r3 = [x + barwidth for x in r2]
    
    # create plot
    plt.xticks(rotation='vertical', fontsize=5)
    plt.ylim(0, maxval)
    plt.bar(r2, merged['sum_x'], color='b', width=barwidth, label='2019')
    plt.bar(r3, merged['sum_y'], color='r', width=barwidth, label='2020')
    plt.xticks([r + barwidth for r in range(len(merged['MM-DD']))], merged['MM-DD'])
    plt.title('VIIRS active fires on ' + i)
    plt.ylabel('Number of active fires / thermal anomalies')
    plt.xlabel('Date')
    plt.legend(loc='upper left')
    
    # create output figure name
    figname = fig_fp + '\\' + i + '.png'
    # save figure
    plt.savefig(figname, dpi=75, format='png')
    # clear plot
    plt.clf()












