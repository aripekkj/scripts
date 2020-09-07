# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 12:11:55 2020


Weighted mean in spatial join

Note: not ready

@author: aripekkj
"""

import pandas as pd
import geopandas as gpd


# filepath
fp = r'E:\LocalData\aripekkj\ProtectedAreas\Madagascar\INSTAT\mdg_adm1_region_df.shp'
fp2 = r'E:\LocalData\aripekkj\ProtectedAreas\Madagascar\WDPA\WDPA_June2020_Mada_final_PAs2.shp'
out_fp = r'E:\LocalData\aripekkj\ProtectedAreas\Madagascar\INSTAT\mdg_adm1_region_df_test_overlay.shp' 

# read file
region = gpd.read_file(fp)
pa = gpd.read_file(fp2)

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

# empty column for area proportion
region_utm['area_prop'] = ""

# loop through wdpa_pid in region_utm DataFrame and select corresponding PA from WDPA layer. Then compute the percentage how much the region covers of the whole PA
for idx, row in region_utm.iterrows():
    # select row from WDPA
    sel = pa_utm[pa_utm['WDPA_PID'] == row['WDPA_PID']]
    region_area_prop = row['area_km2'] / sel['area_km2']
    region_utm['area_prop'].iloc[idx] = region_area_prop.iloc[0]
    
region_utm['area_prop']


















