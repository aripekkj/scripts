# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 11:19:18 2020

Plot sum of daily data over daily average from previous years. 
Script made using VIIRS active fire data from S-NPP satellite

Script produces barplot from input files and saves only the plot.

Notes:  -geopandas clip is slow
            UPDATE: newer version of geopandas (0.8.0) has experimental implementation of pygeos library to improve efficiency
        See https://jorisvandenbossche.github.io/blog/2017/09/19/geopandas-cython/ explains the bottleneck issue

        -Could replace parts of the script with functions to avoid repeating 

@author: Ap
"""

import pandas as pd
import geopandas as gpd
import glob
import numpy as np
import matplotlib.pyplot as plt
import pygeos

# filepath for shapefiles where to calculate mean
fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\fire15_19\*.shp' # *look for shapefiles
# filepath for shapefile to compare to the mean
fp2 = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\2020\fire_mar_jun_2020.shp'
# filepath for polygon
fp3 = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\WDPA\WDPA_Oct2019_Land_0_1manualClean.shp'
# filepath for figure output
fig_dir = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\figures\Madagascar'

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

# dataframe list
df_list = []

# list of column names
colnames_1519 = ['2015', '2016', '2017', '2018', '2019']

# read shapefiles to list
for file in glob.glob(fp):
    shp = gpd.read_file(file)
    df_list.append(shp)

############ Calculate mean ##############

# read polygon file
poly = gpd.read_file(fp3)

# read file
fire20 = gpd.read_file(fp2)
    
# set running number
i = 0

# continuous loop for the length of poly GeoDataFrame
while i < len(poly):
    # read single polygon from poly GeoDataFrame
    single_poly = poly.iloc[[i]]
    
    # Empty dataframe for merging
    merged = pd.DataFrame()
    
    # set counter
    counter = 1
    
    # loop through shapefiles in list
    for f in df_list:
        # read file
        gdf = f
        # select rows where CONFIDENCE is not 'l'
        sel = gdf[gdf['CONFIDENCE'] != 'l']
        # keep only relevant columns
        sel = sel[['LATITUDE', 'LONGITUDE', 'ACQ_DATE', 'geometry']]
        # clip selected by polygon
        clip = gpd.clip(sel, single_poly)
        
        # if the GeoDataFrame is empty, return to beginning of the loop
        if len(clip) == 0:
            print('empty dataframe, ' + str(counter) + '/' + str(len(df_list)))
            if counter == 5:
                break
            else:
                counter += 1
                continue
        
        # create date range
        clip['datetime'] = pd.to_datetime(clip['ACQ_DATE'], format='%Y-%m-%d')
        year = clip['ACQ_DATE'].values[0][0:4]
        daterange = pd.date_range(str(year + '-03-01'), str(year + '-06-30'))
        
        # group by date using the function
        grouped = groupByDate(clip, daterange)
        
        # reset index
        grouped = grouped.reset_index()
        
        # rename columns    
        y = str(grouped[grouped.columns[0]].values[0])[:4] # take year from first column
        grouped = grouped.rename(columns={grouped.columns[0]: y, grouped.columns[1]: grouped.columns[1] + y}) # rename
    
        if len(merged) == 0:
            merged = grouped    
        else:
            # merge
            merged = pd.merge(merged, grouped, how='inner', left_index=True, right_index=True)
        
        print(str(counter) + '/' + str(len(df_list)))
        counter += 1
    
    #print(merged)

    
    merged_columns = merged.columns    
    
    # check if all years are present in the data
    for a in colnames_1519:
        if a in merged_columns:
            print(str(a) + ' found')
        else:
            # create data for year that was not found in columns
            print('Creating data for ' + str(a))
            missing_daterange = pd.date_range(str(a + '-03-01'), str(a + '-06-30'))
            merged = merged.assign(yr=missing_daterange)
            merged = merged.rename(columns={'yr': a}) # rename
            # create also 'sum' solumn with 0 values
            colname = 'sum' + str(a)
            merged['new_col'] = 0
            merged = merged.rename(columns={'new_col':colname})
                
    # calculate daily averages
    merged['avg'] = merged[['sum2015', 'sum2016', 'sum2017', 'sum2018', 'sum2019']].mean(axis=1)
    
    # create new column 'MM-DD' for month and day 
    merged['MM-DD'] = pd.to_datetime(merged['2019']).dt.strftime('%m-%d')
    

    ########## Process data that is compared to the mean ############
    
        
    # select rows where 'CONFIDENCE' is not 'l'
    sel20 = fire20[fire20['CONFIDENCE'] != 'l']
    
    # keep only relevant columns
    sel20 = sel20[['LATITUDE', 'LONGITUDE', 'ACQ_DATE', 'geometry']]
    # clip selected by polygon
    clip20 = gpd.clip(sel20, single_poly)
    
    # create daterange and group data if the 2020 data has records
    if len(clip20) != 0:
        
        # create date range
        clip20['datetime'] = pd.to_datetime(clip20['ACQ_DATE'], format='%Y-%m-%d')
        year20 = clip20['ACQ_DATE'].values[0][0:4]
        daterange20 = pd.date_range(str(year20 + '-03-01'), str(year20 + '-06-30'))
        
        # group by date
        grouped20 = groupByDate(clip20, daterange20)
        
        # reset index
        grouped20 = grouped20.reset_index()
        
        # rename columns  
        y20 = str(grouped20[grouped20.columns[0]].values[0])[:4] # take year from first column
        grouped20 = grouped20.rename(columns={grouped20.columns[0]: y20, grouped20.columns[1]: grouped20.columns[1] + y20}) # rename
        
        # create new column 'MM-DD' for month and day 
        grouped20['MM-DD'] = grouped20['2020'].dt.strftime('%m-%d')
    
    # create null data if 2020 data doesn't have records
    else:
        grouped20 = pd.DataFrame()
        year20 = '2020'
        daterange20 = pd.date_range(str(year20 + '-03-01'), str(year20 + '-06-30'))
        grouped20 = grouped20.assign(yr=daterange20)
        grouped20 = grouped20.rename(columns={'yr': year20}) # rename
        # create also 'sum' solumn with 0 values
        colname = 'sum' + str(year20)
        grouped20['new_col'] = 0
        grouped20 = grouped20.rename(columns={'new_col':colname})
    
    ######### PLOT ############
    
    copyright_string = 'Digital Geography Lab / Ari-Pekka Jokinen'
    
    # plot
    barwidth=0.25
    
    r1 = np.arange(len(merged['MM-DD']))
    r2 = [x + barwidth for x in r1]
    r3 = [x + barwidth for x in r2]
    
    plt.xticks(rotation='vertical', fontsize=3)
    plt.ylim(0,50)
    plt.bar(r2, merged['avg'], color='b', width=barwidth, label='2015-2019 average')
    plt.bar(r3, grouped20['sum2020'], color='r', width=barwidth, label='2020')
    plt.xticks([r + barwidth for r in range(len(merged['MM-DD']))], merged['MM-DD'])
    plt.title('FIRMS VIIRS active fires on ' + str(single_poly['NAME'].iloc[0]))
    plt.ylabel('Number of active fires / thermal anomalies')
    plt.xlabel('Date')
    plt.legend(loc='upper left')
    #plt.text(len(r1),-100, s=copyright_string, horizontalalignment='right', fontsize=5)
    
    fig_fp = fig_dir + '\\' +  str(single_poly['NAME'].iloc[0]) + '.png' 
    plt.savefig(fig_fp, dpi=100, format='png')
    
    # clear plot
    plt.clf()

    # print progression
    print('Processed ' + str(i+1) + '/' + str(len(poly)))
    # increase i
    i += 1
    







