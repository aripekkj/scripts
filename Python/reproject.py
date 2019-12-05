# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 09:50:00 2019

reproject raster files from filelist

@author: aripekkj
"""

# modules
import numpy as np
import rasterio
import geopandas as gpd
from rasterio.warp import calculate_default_transform, reproject, Resampling

# filepaths
fp = r'E:\LocalData\aripekkj\TA\Bhutan\Hansen\lossyear\Hansen_GFC2015_lossyear_merge_clip.tif'
out_fp = r'E:\LocalData\aripekkj\TA\Bhutan\Hansen\lossyear\Hansen_GFC2015_lossyear_merge_clip_utm46.tif'

# set destination coordinate system
dst_crs = 'EPSG:32646'

with rasterio.open(fp) as src:
    transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
            })
    
    with rasterio.open(out_fp, 'w', **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)




# +proj=utm +zone=46 +datum=WGS84 +units=m +no_defs







