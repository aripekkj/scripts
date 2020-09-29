# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 14:51:02 2020

stack dataframe and concat to another already stacked dataframe


@author: aripekkj
"""


import pandas as pd


# filepath 
fp1 = r'E:/LocalData/aripekkj/ProtectedAreas/Precipitation/WDPA_Mada_Precip_20112020.csv'
fp2 = r'E:/LocalData/aripekkj/ProtectedAreas/model/covidpasfireMATTI_final.txt'
out_fp = r'E:/LocalData/aripekkj/ProtectedAreas/model/WDPA_Fire_Precip_Monthly_2011_2020.csv'


# read file
df = pd.read_csv(fp1, sep=",")

# Valitaan vain 2011 sadekuukaudet
df = df.iloc[:,0:15]

df = df.set_index(['WDPAID', 'NAME', 'GIS_AREA']).stack()
df = df.reset_index()
df

# year and month column
df['Year'] = df['level_3'].str[0:4].astype('int64')
df['Month'] = df['level_3'].str[4:6].astype('int64')

df

# rename columns
df = df.rename(columns={0:'Precipitation'})

# read file
df2 = pd.read_csv(fp2, sep="\t")
df2.head()

# take subsets of dfs
df_sub = df[['NAME', 'Year', 'Month', 'Precipitation']]
df2_sub = df2[['NAME', 'Fires_sum', 'Year', 'Month', 'Precipitation', 'YEAR_CREAT', 'Biome']]

# check df datatypes
df_sub.dtypes
df2_sub.dtypes

# change df_sub columns to same dtypes
df_sub['Precipitation'] = df_sub['Precipitation'].astype('float64')

# concatenate df subsets
df_conc = pd.concat([df_sub, df2_sub], ignore_index=True)

# write as csv file
df_conc.to_csv(out_fp, sep=";")







