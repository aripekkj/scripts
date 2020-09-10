#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 14:26:34 2020

Plotting glacier centerline elevations

Updates: 28/1
    plotting different elevation datasets works with different line lengths.
    Very rough and manual. 
    
    To Do: create functions to make using iteratively possible

@author: apj
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
from shapely.geometry import Point, LineString
from scipy.spatial import distance
import numpy as np
import ogr

# set filepath
fp = r'/Users/apj/Documents/_HY/Greenland/centerlines/all_centerline_3d_points/cl_rgi_points_all_elevs_clipped.shp'

# function to get coordinate list
def getCoords(dframe):
    # empty list for coordinates
    coord_list = []
    for i in sel['geometry']:
        p = str(i)
        multipoint = ogr.CreateGeometryFromWkt(p)
        point = multipoint.GetGeometryRef(0)
        xy = point.GetX(), point.GetY()
        coord_list.append(xy)
    return coord_list

# function to calculate line length
def calculateLength(coordinate_list):
    # calculate distances between points to a list
    d = 0
    lengths = []
    while d < len(coordinate_list):
        if d == 0:
            dist = 0
        elif d >= 1:
            dist = distance.euclidean(coordinate_list[d-1], coordinate_list[d])
        elif d == len(coordinate_list):
            break
        #print(dist)
        lengths.append(dist)        
        d += 1
    # return list of euclidean distances between points
    return lengths


# read file
df = gpd.read_file(fp)

# check column names
df.columns

# get unique field id's to list
unique_orig_fids = list(df['ORIG_FID'].unique())

# counter
counter = 1

# loop through unique IDs and create plots
for orig_id in unique_orig_fids:
    
    # select by orig_fid
    sel = df[df['ORIG_FID'] == orig_id]
    
    # get coordinates
    coords = getCoords(sel)
    
    # get length between points
    length_between_points = calculateLength(coords)
    
    # assign lengths to new column in dataframe subselection
    sel = sel.assign(lengths=length_between_points)
    
    # compute cumulative length
    sel['cum_length'] = np.cumsum(length_between_points)
    # length in km
    sel['cum_length_km'] = sel['cum_length'] / 1000
    
    
    # plot elevations and glacier length with matplotlib
    plt.plot(sel['cum_length_km'], sel['Elev_50s'], 'r-')
    plt.plot(sel['cum_length_km'], sel['Elev_80s'], 'b-')
    plt.plot(sel['cum_length_km'], sel['Elev_2010s'], 'g-')
    #plt.plot(line_subset['cum_length'], line_subset['ArcticDEM_'], 'g-')
    plt.title('Glacier centerline elevations for glacier: ' + str(sel['RGIID'].iloc[0]) )
    plt.xlabel('distance (km)')
    plt.ylabel('elevation (m)')
    plt.legend(['New 1950s DEM', 'AERODEM', 'Pilot DEM'], loc='upper right')
    plt.show
        
    """
    Saving figure
    """
    # define filename and filepath for the figure and save figure
    figname = 'cl_' + str(sel['RGIID'].iloc[0]) + '.png'
    out_path = r'/Users/apj/Documents/_HY/Greenland/centerlines/figures/'
    figpath = os.path.join(out_path, figname)
    plt.savefig(figpath, format = 'png')
    
    # pause before closing the figure
    plt.pause(0.5)
    plt.close()
    print(str(counter) + ' / ' + str(len(unique_orig_fids)))
    counter += 1















