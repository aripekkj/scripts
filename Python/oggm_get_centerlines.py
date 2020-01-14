#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 10:01:49 2019

@author: apj
"""

# import packages
import gdal
import numpy as np
from oggm import cfg
import geopandas as gpd
from functools import partial, wraps
from shapely.ops import transform as shp_trafo
from salem import wgs84

# create configuration file
cfg.initialize()

# locate configuration file
cfg.CONFIG_FILE



# test run. Read the parameter file and make it available for tools.
from oggm import cfg, utils
cfg.initialize(logging_level='WORKFLOW')

# some parameters
cfg.PARAMS['continue_on_error'] = True
cfg.PARAMS['border'] = 10


""" Workflow """
from oggm import workflow

# set working directory
#cfg.PATHS['working_dir'] = utils.gettempdir(dirname='OGGM-GettingStarted', reset=True)
cfg.PATHS['working_dir'] = '/Users/apj/OGGM/'
cfg.PATHS['working_dir']

# Define glaciers for the run. These are called by Randolph glacier inventory id
#rgi_ids = ['RGI60-11.01328', 'RGI60-11.00897']
rgi_ids = ['RGI60-05.01125']




######### Select glaciers inside a polygon
# 1 read shapefile
fp = r'/Users/apj/OGGM/disko_nuussuaq_area_test_wgs84.shp'
shape = gpd.read_file(fp)
shape.columns
shape['RGIId'].head()

# assign RGI Ids to list



# Glacier directories
gdirs = workflow.init_glacier_regions(shape, from_prepro_level=1, prepro_border=80, prepro_rgi_version='61', from_tar=True)

# look contents of gdirs
type(gdirs)

# access item on the gdirs list
gdir = gdirs[0]  # 
print('Path to the DEM:', gdir.get_filepath('dem'))

# look at the attributes of the glacier
gdir
gdir.rgi_date # date at which the outlines are valid

# plot the glacier location and outline
from oggm import graphics
graphics.plot_googlemap(gdir, figsize=(8, 7))

""" Tasks """
from oggm import tasks

# run the glacier_masks task on all gdirs
workflow.execute_entity_task(tasks.glacier_masks, gdirs);

# the command wrote a new file in our glacier directory, providing raster masks of the glaciers
print('Path to the masks:', gdir.get_filepath('gridded_data'))

# It is also possible to apply several tasks sequentially (i.e. one after an other) on our glacier list:
list_talks = [
         tasks.compute_centerlines,
         tasks.initialize_flowlines,
         tasks.compute_downstream_line,
         ]
for task in list_talks:
    # The order matters!
    workflow.execute_entity_task(task, gdirs)

# plot the results
graphics.plot_centerlines(gdir, figsize=(8, 7), use_flowlines=True, add_downstream=True)

# the glacier directories now have more files in them. Let's look
import os
print(os.listdir(gdir.dir))


# export centerlines to shapefiles
test = gdir.read_pickle('centerlines')
olist = []
for j, cl in enumerate(test[::-1]):
        mm = 1 if j == 0 else 0
        gs = gpd.GeoSeries()
        gs['RGIID'] = gdir.rgi_id
        gs['LE_SEGMENT'] = np.rint(np.max(cl.dis_on_line) * gdir.grid.dx)
        gs['MAIN'] = mm
        tra_func = partial(gdir.grid.ij_to_crs, crs=wgs84)
        gs['geometry'] = shp_trafo(tra_func, cl.line)
        olist.append(gs)

# centerlines GeoDataFrame
cl_gdf = gpd.GeoDataFrame()

# assign linestrings from GeoSeries to GeoDataFrame
for i in olist:
    cl_gdf.append(i, ignore_index=True)

# write GeoDataFrame to Shapefile
cl_gdf.to_file('centerlines.shp', driver='ESRI Shapefile')
