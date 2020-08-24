# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 11:19:18 2020

Plot sum of daily data over daily average from previous years. 
Script made using VIIRS active fire data from S-NPP satellite

Script produces barplot from input files and saves only the plot.
Should be possible to produce VIIRS S-NPP results for other areas just by editing filepaths and figure texts (taken that .shp files have same crs)

Notes:  -geopandas clip is slow, but overlay function works only on polygons so no easy
        work around here.
        See https://jorisvandenbossche.github.io/blog/2017/09/19/geopandas-cython/ for possible solution
        -Could replace parts of the script with functions to avoid repeating 

@author: Ap
"""

import pandas as pd
import geopandas as gpd
import glob
import numpy as np
import matplotlib.pyplot as plt

# filepath for shapefiles where to calculate mean
fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\fire15_19\*.shp' # *look for shapefiles
# filepath for shapefile to compare to the mean
fp2 = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\fire_01032020_30062020_Madagascar_PAs.shp'
# filepath for polygon
fp3 = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\WDPA\WDPA_Oct2019_Land_0_1manualClean.shp'
# filepath for figure output
fig_fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\figures\Madagascar'

# function to count sum and group them by day
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
    #df_out['cumsum'] = df_out['sum'].cumsum()
    
    return df_out;


############ Calculate mean ##############

# read polygon file
poly = gpd.read_file(fp3)

# Empty dataframe for merging
merged = pd.DataFrame()

# set counter
counter = 0

# loop through shapefiles in directory
for file in glob.glob(fp):
    # read file
    gdf = gpd.read_file(file)
    # select rows where CONFIDENCE is not 'l'
    sel = gdf[gdf['CONFIDENCE'] != 'l']
    # keep only relevant columns
    sel = sel[['LATITUDE', 'LONGITUDE', 'ACQ_DATE', 'geometry']]
    # clip selected by polygon
    clip = gpd.clip(sel, poly)
    
    # create date range
    clip['datetime'] = pd.to_datetime(clip['ACQ_DATE'], format='%Y-%m-%d')
    year = clip['ACQ_DATE'].values[1][0:4]
    daterange = pd.date_range(str(year + '-03-01'), str(year + '-06-14'))
    
    # group by date using the function
    grouped = groupByDate(clip, daterange)
    
    # reset index
    grouped = grouped.reset_index()
    
    # rename columns    
    y = str(grouped[grouped.columns[0]].values[0])[:4] # take year from first column
    grouped = grouped.rename(columns={grouped.columns[0]: y, grouped.columns[1]: grouped.columns[1] + y}) # rename

    if counter == 0:
        merged = grouped    
    else:
        # merge
        merged = pd.merge(merged, grouped, how='inner', left_index=True, right_index=True)
    
    print(counter)
    counter += 1


# calculate daily averages
merged['avg'] = merged[['sum2015', 'sum2016', 'sum2017', 'sum2018', 'sum2019']].mean(axis=1)

# create new column 'MM-DD' for month and day 
merged['MM-DD'] = merged['2019'].dt.strftime('%m-%d')


########## Process data that is compared to the mean ############

# read file
fire20 = gpd.read_file(fp2)

# select rows where 'CONFIDENCE' is not 'l'
sel20 = fire20[fire20['CONFIDENCE'] != 'l']

# keep only relevant columns
sel20 = sel20[['LATITUDE', 'LONGITUDE', 'ACQ_DATE', 'geometry']]
# clip selected by polygon
clip20 = gpd.clip(sel20, poly)

# create date range
clip20['datetime'] = pd.to_datetime(clip20['ACQ_DATE'], format='%Y-%m-%d')
year20 = clip20['ACQ_DATE'].values[1][0:4]
daterange20 = pd.date_range(str(year20 + '-03-01'), str(year20 + '-06-14'))

# group by date
grouped20 = groupByDate(clip20, daterange20)

# reset index
grouped20 = grouped20.reset_index()

# rename columns  
y20 = str(grouped20[grouped20.columns[0]].values[0])[:4] # take year from first column
grouped20 = grouped20.rename(columns={grouped20.columns[0]: y20, grouped20.columns[1]: grouped20.columns[1] + y20}) # rename

# create new column 'MM-DD' for month and day 
grouped20['MM-DD'] = grouped20['2020'].dt.strftime('%m-%d')
print(grouped20.head())
######### PLOT ############

# plot
barwidth=0.25

r1 = np.arange(len(merged['MM-DD']))
r2 = [x + barwidth for x in r1]
r3 = [x + barwidth for x in r2]

plt.xticks(rotation='vertical', fontsize=5)
plt.bar(r2, merged['avg'], color='b', width=barwidth, label='2015-2019 average')
plt.bar(r3, grouped20['sum2020'], color='r', width=barwidth, label='2020')
plt.xticks([r + barwidth for r in range(len(merged['MM-DD']))], merged['MM-DD'])
plt.title('FIRMS VIIRS data on Cambodia protected areas')
plt.ylabel('Number of active fires / thermal anomalies')
plt.xlabel('Date')
plt.legend(loc='upper left')
plt.text(len(r1),-10, 'right top', text='Digital Geography Lab / Ari-Pekka Jokinen', 
         horizontalalignment='right', fontsize=5)

plt.savefig(fig_fp, dpi=75, format='png')










