# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 12:11:55 2020


Compute area weighted mean for areas in spatial join



@author: aripekkj
"""

import pandas as pd
import geopandas as gpd


# filepath
fp = r'E:\LocalData\aripekkj\ProtectedAreas\Madagascar\INSTAT\mdg_adm1_region_df.shp'
fp2 = r'E:\LocalData\aripekkj\ProtectedAreas\Madagascar\WDPA\WDPA_June2020_Mada_final_PAs2.shp'
fp3 = r'E:\LocalData\aripekkj\ProtectedAreas\Madagascar\sjoin\WDPA_fire_w_region_df_pop_acc_means_finalPAs.shp'
out_fp = r'E:\LocalData\aripekkj\ProtectedAreas\Madagascar\INSTAT\mdg_adm1_region_df_w_spatial_join.shp' 

# read file
region = gpd.read_file(fp)
pa = gpd.read_file(fp2)
join_pa = gpd.read_file(fp3)

# overlay region by wdpa. result has attributes from both layers and areas where single PA polygon intersects over many regions are individual polygons
region_ol = gpd.overlay(region, pa) 

# function for reprojecting
def reProject(shapefile, epsg_code):
    region_copy = shapefile.copy()
    region_reproj = region_copy.to_crs(epsg=epsg_code)
    return region_reproj

# copy and transform GeoDataFrame to cartesian system to get area calculations in meters
region_utm = reProject(region_ol, 32738)
pa_utm = reProject(pa, 32738)

# compute area in square kilometers
region_utm['area_km2'] = region_utm['geometry'].area / 10**6 
pa_utm['area_km2'] = pa_utm['geometry'].area / 10**6

# empty column for area proportion. This will be used as weight
region_utm['area_prop'] = ""

# loop through wdpa_pid in region_utm DataFrame and select corresponding PA from WDPA layer. Then compute the percentage how much the region covers of the whole PA
for idx, row in region_utm.iterrows():
    # select row from WDPA
    sel = pa_utm[pa_utm['WDPA_PID'] == row['WDPA_PID']]
    region_area_prop = row['area_km2'] / sel['area_km2']
    region_utm['area_prop'].iloc[idx] = region_area_prop.iloc[0]
    
region_utm['area_prop']

# compute weighted mean for INSTAT columns
region_utm['Econ_det_w'] = region_utm['Econ_deter'] * region_utm['area_prop']
region_utm['Nr_of_HH_w'] = region_utm['Nr_of_HH'] * region_utm['area_prop']
region_utm['PoorFood_w'] = region_utm['Poor_food_'] * region_utm['area_prop']
region_utm['noFoodAl_w'] = region_utm['no_food_al'] * region_utm['area_prop']
region_utm['FoodSecA_w'] = region_utm['food_sec_a'] * region_utm['area_prop']


# function to count sum and group them by WDPA_PID
def groupBy(df, column_name):
    
    # group by WDPA_PID
    df_group = df.groupby('WDPA_PID')[column_name].sum()
    
    # convert Series to DataFrame
    df_out = pd.Series.to_frame(df_group)
    # reset index
    df_out = df_out.reset_index()
    
    return df_out;

# group by
econ_det_w_sum = groupBy(region_utm, 'Econ_det_w')
nrHH_w = groupBy(region_utm, 'Nr_of_HH_w')
poorfood_w = groupBy(region_utm, 'PoorFood_w')
noFood_w = groupBy(region_utm, 'noFoodAl_w')
FoodSecA_W = groupBy(region_utm, 'FoodSecA_w')

# join list
join_list = [econ_det_w_sum, nrHH_w, poorfood_w, noFood_w, FoodSecA_W]

# join grouped dataframes by wdpa id 
for i in join_list:
    
    join_pa = pd.merge(join_pa, i, how='outer', on='WDPA_PID')

# save to shapefile
join_pa.to_file(out_fp, driver='ESRI Shapefile')



# to find certain protected area for double checking results
test = region_utm[region_utm['WDPA_PID'] == '555548845']
print(test[['Econ_deter', 'area_km2', 'area_prop', 'Econ_det_w']])
print(sum(test['Econ_deter']) / len(test['Econ_deter']))
print(sum(test['Econ_det_w']))





















