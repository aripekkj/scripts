# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 10:47:12 2020

Select points that fall inside selected grid polygons. Copy the .tif files corresponding the points to a directory


@author: aripekkj
"""

import pandas as pd
import geopandas as gpd
import os
import shutil
import matplotlib.pyplot as plt

# set working directory
os.chdir(r'E:\LocalData\aripekkj\Greenland')

# set filepath for input files
fp_grid = r'E:\LocalData\aripekkj\Greenland\Area_grid\grid.gpkg'
fp_pts = r'E:\LocalData\aripekkj\Greenland\scanned_images\nuussuaq_50k_land_utm22.gpkg'
gcp_fp = r'E:\LocalData\aripekkj\Greenland\GCPs\GCPs_dem.shp'


# read files
grid = gpd.read_file(fp_grid)
pts = gpd.read_file(fp_pts)
gcp = gpd.read_file(gcp_fp)

########### SELECT GRIDS ############

# Grid ids to be selected
grid_ids = [96]

# make a grid string for filenames
gridstring = ''.join(map(str,grid_ids))

# Do selection using pandas isin()
grid_sel = grid[grid.id.isin(grid_ids)]
# check result
grid_sel

######## CLIPPING #############

# make unary union for grid polygons
poly = grid_sel.unary_union
pts_sel = pts[pts.geometry.intersects(poly)]

# clip gcp file
gcp_sel = gcp[gcp.geometry.intersects(poly)]
# write to file
#gcp_filename = "GCP_grid" + gridstring
gcp_sel.to_file('GCPs_grid96.shp', driver='ESRI Shapefile')
# export gcp also as csv
gcp_sel.to_csv('GCP_grid96.csv', sep=',')

############ FIND TIFF FILES AND COPY THEM TO DIRECTORY ###################

# make a list of filenames 
fnames = pts_sel['filename'].values.tolist()

# set directory where to start looking for files
startdir = r'F:\GreenlandAerialPhotos'

# set destination directory
destdir = r'F:\AerialPhotoSubsets'

# browse through folders and print files that meet the conditions
for root, dirs, files in os.walk(startdir):
    for name in files:
        # this check if any of the filenames in fnames list matches the currently browsed file
        if any(fn in name for fn in fnames):
            # check if the file has 'rcr' string in its name
            if 'rcr' in name:
                # get filepath for the current file and copy file to directory
                fp = os.path.join(root,name)
                shutil.copy(fp, destdir)
                
########### WRITE IMAGE GEOLOCATION CSV #####################
                
# For Pix4D should be in format filename;X;Y;Z
image_loc = pts_sel[['filename', 'utm22_x', 'utm22_y']]

# update filename with .tif file extension
image_loc['filename'] = image_loc['filename'] + '.tif'

# save as csv
image_loc.to_csv('Image_loc_grid96.csv', sep=';', header=False, index=False)






