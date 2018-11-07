#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merging rasters

Created on Fri Nov  2 10:33:26 2018

@author: apj
"""


# import modules
import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import glob
import os

# set filepaths. Variables with same name are ment for different projects
#dirpath = r'/Users/apj/Documents/_HY/DEM_artefact_detection/ArcticDemRasti/ArcticDEM_processed/'
#out_fp = r'/Users/apj/Documents/_HY/DEM_artefact_detection/ArcticDemRasti/Merged/ArcticDEM_merged.tif'

# 
dirpath = r"/Users/apj/Documents/_HY/Kurssit/Glacier_deposits_terrains_and_deglaciation_dynamics/data/3/"
out_fp = r"/Users/apj/Documents/_HY/Kurssit/Glacier_deposits_terrains_and_deglaciation_dynamics/data/3_merged_lzw.tif"


# search criteria for files
search_criteria = '*.tif'
q = os.path.join(dirpath, search_criteria)
print(q)

# list files with glob function
dem_fps = glob.glob(q)
dem_fps

# empty list for files that will be included in mosaic
src_files_to_mosaic = []

# open the files in rasterio using for loop
for fp in dem_fps:
    src = rasterio.open(fp)
    src_files_to_mosaic.append(src)

# check
src_files_to_mosaic


# create merge mosaic
mosaic, out_trans = merge(src_files_to_mosaic)

# copy metadata
out_meta = src.meta.copy()

out_meta

# update metadata
out_meta.update({"driver": "GTiff",
                  "height": mosaic.shape[1],
                  "width": mosaic.shape[2],
                  "transform": out_trans,
                  "crs": "+proj=utm +zone=35 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
                  }
                 )

# proj4 Polar stereographic north
# "crs": "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs "
                  

# write file
with rasterio.open(out_fp, "w", **out_meta, compress = "LZW") as dest:
    dest.write(mosaic)













