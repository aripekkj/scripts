#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 14:26:34 2020

Plotting glacier centerline elevations

@author: apj
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
from shapely.geometry import Point, LineString
from scipy.spatial import distance
import numpy as np

# set filepath
fp = r'/Users/apj/Documents/_HY/Greenland/centerlines/centerlines_w_3elevs.shp'

# read file
lines = gpd.read_file(fp)

# check data
lines.head()
lines.columns

# subset data so that only main trunks of the glaciers are selected ('MAIN' == 1)
main_trunks = lines.loc[lines['MAIN'] == 1]

# check data
main_trunks.columns
main_trunks.head()

# get unique RGI IDs 
unique_rgi_ids = lines.RGIID.unique()

# this is for testing
kuannersuit_id = ['RGI60-05.01456']

# plotting the centerline elevations one by one
for i in unique_rgi_ids[:10]:
    # make a subset using RGI IDs
    line_subset = main_trunks.loc[main_trunks['RGIID'] == i]

    """
    To get length of the glacier centerline, distances between Point geometries
    needs to be calculated
    """
    # empty list for coordinate tuples
    coord_list = []
    
    # add z value to point geometry
    for a, b in zip(line_subset.geometry, line_subset.aerodem_19):
        #print(a, b)
        coord_list.append((a.x, a.y, b))

    # new column for xyz coordinates
    line_subset['xyz'] = pd.Series(coord_list)

    # calculate distances between points to a list
    d = 0   
    lengths = []
    while d < len(coord_list):
        if d == 0:
            dist = 0
        elif d >= 1:
            dist = distance.euclidean(coord_list[d-1], coord_list[d])
        elif d == len(coord_list):
            break
        #print(dist)
        lengths.append(dist)        
        d += 1
    
    # add lengths to new column
    line_subset['lengths'] = pd.Series(lengths)
    
    # count cumulative length to a new column
    line_subset['cum_length'] = np.cumsum(lengths)
    
    # plot elevations and glacier length with matplotlib
    plt.plot(line_subset['cum_length'], line_subset['aerodem_19'], 'r-')
    plt.plot(line_subset['cum_length'], line_subset['gimp_utm22'], 'b-')
    plt.plot(line_subset['cum_length'], line_subset['ArcticDEM_'], 'g-')
    plt.title('Glacier centerline elevations for glacier: ' + i)
    plt.xlabel('distance (m)')
    plt.ylabel('elevation (m)')
    plt.legend(['AERODEM', 'GIMP', 'ArcticDEM'], loc='upper right')
    
    plt.show
    
    """
    Saving figure
    """
    # define filename and filepath for the figure and save figure
    #figname = 'cl_' + i + '.png'
    #out_path = r'/Users/apj/Documents/_HY/Greenland/centerlines/figures/'
    #figpath = os.path.join(out_path, figname)
    #plt.savefig(figpath, format = 'png')
    
    # pause before closing the figure
    plt.pause(0.5)
    plt.close()

















