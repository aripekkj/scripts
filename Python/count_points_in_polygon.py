# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 14:36:49 2020

@author: Ap
"""

import pandas as pd
import geopandas as gpd
import glob

# filepath
fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\fire15_19\*.shp'
fp2 = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\Madagascar\2020\fire_mar_jun_2020.shp'
poly = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\WDPA\WDPA_June2020_Mada_final_PAs2.shp'
outfp = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\WDPA\WDPA_VIIRSfire_sums_mar_jun_1520_finalPAs.shp'

# read polygons
polys = gpd.read_file(poly)

# empty list for dataframes
df_list = []

# read shapefiles to list
for file in glob.glob(fp):
    shp = gpd.read_file(file)
    # select rows where CONFIDENCE is not 'l'
    shp = shp[shp['CONFIDENCE'] != 'l']
    df_list.append(shp)

# read 2020 data
fire20 = gpd.read_file(fp2)
# select rows where CONFIDENCE is not 'l'
fire20 = fire20[fire20['CONFIDENCE'] != 'l']

# append also 2020 data to df list
df_list.append(fire20)

# copy of polygons where to merge result
polys_result = polys

# loop dataframes and create spatial join to polygons
for df in df_list:
    # spatial join
    sj = gpd.sjoin(df, polys, op='within')
    # get year
    y = sj['ACQ_DATE'].iloc[0][:4]
    # group by area name
    grouped = sj.groupby('NAME').size()
    # grouped to dataframe
    group_df = grouped.to_frame().reset_index()
    # name columns
    group_df.columns = ['NAME', str('sum'+y)]
    # merge result back to polygons
    polys_result = polys_result.merge(group_df, on='NAME', how='outer')

# replace NaN values with 0
polys_result = polys_result.fillna(0)

# calculate average from 2015-2019 sums to new column
cols = polys_result.loc[: , 'sum2015':'sum2019'] # select columns 
# calculate mean
polys_result['avg1519'] = cols.mean(axis=1)
# calculate difference between 2020 and the average as 2020 - avg1519 to see 
# whether 2020 is greater than average or not
polys_result['diff_2020_avg'] = polys_result['sum2020'] - polys_result['avg1519'] 

# function to categorize difference column values
def setValue(row):
    if row['diff_2020_avg'] == 0:
        value = 0
    elif row['diff_2020_avg'] > 0:
        value = 1
    else:
        value = -1
    return value

# create new column by applying function
polys_result['cat'] = polys_result.apply(setValue, axis=1)

# save result to file
polys_result.to_file(outfp, driver='ESRI Shapefile')



















