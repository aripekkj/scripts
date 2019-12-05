# -*- coding: utf-8 -*-
"""
Clip raster by extent (either polygon or bounding box)

This script is for clipping raster files 



"""


# import tools
import pandas as pd
import numpy as np
import os
import glob

import rasterio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg
import pycrs


# set filepaths
fp = r'E:\LocalData\aripekkj\TA\Bhutan\Hansen\lossyear\Hansen_GFC2015_lossyear_merge.tif'
fp_shape = r'E:\LocalData\aripekkj\TA\Bhutan\Bhutan_borders\btn_admbnda_adm0_bnlc.shp'

out_tif = r'E:\LocalData\aripekkj\TA\Bhutan\Hansen\lossyear\Hansen_GFC2015_lossyear_merge_clip.tif'

# open raster in read mode
data = rasterio.open(fp)

# plot raster
#show((data, 1), cmap='terrain')

# read shapefile
sh = gpd.read_file(fp_shape)

# check crs of files
data.crs
sh.crs

# create bounding box
#minx, miny = 26.001953839, 69.917662762
#maxx, maxy = 26.451952629, 70.054088643

#bbox = box(minx, miny, maxx, maxy)

# create geodataframe of the bounding box
#geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))

# reproject to same CRS as raster
#geo = geo.to_crs(crs=data.crs.data)

# function
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

# get features using function
coords = getFeatures(sh)

print(coords)

# clipping
out_img, out_transform = mask(data, shapes=coords, crop=True)

# Copy the metadata. Just to check here
out_meta = data.meta.copy()
print(out_meta)

# parse epsg code. Rasters in arcticdem are missing 'init' info so this is skipped
# epsg_code = int(data.crs.data['init'][5:])
# print(epsg_code)

# updating metadata
out_meta.update({"driver": "GTiff",
                 "height": out_img.shape[1],
                 "width": out_img.shape[2],
                 "transform": out_transform,
               }
    )
#   metadata update skipped
#   "crs": pycrs.parser.from_epsg_code(epsg_code).to_proj4()

# saving the clipped layer
with rasterio.open(out_tif, "w", **out_meta) as dest:
    dest.write(out_img)






















