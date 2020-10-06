# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 14:48:45 2020

Filter by datetime


@author: aripekkj
"""

import geopandas as gpd


# filepath
fp = r'E:/LocalData/aripekkj/ProtectedAreas/Madagascar/some/flickr_in_wdpa_mada.gpkg'
out_fp = r'E:/LocalData/aripekkj/ProtectedAreas/Madagascar/some/flickr_in_wdpa_mada_20052018.gpkg'

# read file
df = gpd.read_file(fp)
print(len(df))

# select by date_taken between 2005 and 2018
df = df[(df['date_taken'] >= '2005-01-01') & (df['date_taken'] <= '2018-12-31')]
print(len(df))

# write to file
df.to_file(out_fp, driver='GPKG')









