# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 11:53:42 2020

@author: Ap
"""

import pandas as pd
import geopandas as gpd

region_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\border\mdg_admbnda_adm1_BNGRC_OCHA_20181031.shp'
table_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\INSTAT\REVENUS_06.csv'
out_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\INSTAT\mdg_adm1_revenue_singlehh.shp'

# read files
region = gpd.read_file(region_fp)
table = pd.read_csv(table_fp, sep=';')

print(table)
table.columns

# create region id column
print(region)
region.columns
region['ADM1_PCODE'].tail()
region.ADM1_PCODE.unique()

r = region['ADM1_PCODE'].str.split('G',1,expand=True).rename(columns={0:'A',1:'B'})
region['region_code'] = r['B'].astype(str).astype(int)

# select only rows where 'cvhh06_q03' is not na
table = table[table['cvhh06_q03'].notna()]

# count sum by region

table_group = table.groupby('cvhhid_q01')['cvhh06_q03'].mean()
table_out = pd.Series.to_frame(table_group)
table_out = table_out.reset_index()

table_out.head()

# merge to polygons
result = pd.merge(region, table_out, how='outer', left_on='region_code', right_on='cvhhid_q01')

# write to file
result.to_file(out_fp, driver='ESRI Shapefile')


