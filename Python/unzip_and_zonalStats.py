# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 12:24:32 2020

Browse through directory, unzip folder, select certain (raster) file,
loop through single polygons, calculate zonal statistics from the raster files for each polygon 
and store result in GeoDataFrame


Notes: 
    created for extracting precipition zonal stats from NASA TRMM/GPM data

@author: Ap
"""


import glob
import rasterio
from rasterio.plot import show
from rasterstats import zonal_stats
import pandas as pd
import geopandas as gpd
from zipfile import ZipFile
from shapely.geometry import shape

# filepaths 
zip_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Precipitation\Monthly20122020\*.zip'
unzip_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Precipitation\Monthly20122020_unzip'
tiff_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Precipitation\Monthly20122020_unzip\*.tif'
poly_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\WDPA\WDPA_June2020_Mada_final_PAs2.shp'
out_fp = r'C:\Users\Ap\Documents\ProtectedAreas\Precipitation\WDPA_Madagascar_Precip_20122020.shp'

# STEP 1 - Unzip certain files

char_string = 'total.accum'

# browse through directory
for fp in glob.glob(zip_fp):
    # read zipfile
    with ZipFile(fp, 'r') as zipObj:
        # get filenames in the zip folder
        fn_list = zipObj.namelist()
        # loop through filenames
        for zip_name in fn_list:
            # extract file if filename includes character string
            if char_string in zip_name:
                zipObj.extract(zip_name, unzip_fp)



# STEP 2 - Compute zonal statistics for the extracted files

# read polygon file
polys = gpd.read_file(poly_fp)

# select only relevant columns
polys = polys[['WDPAID', 'NAME', 'GIS_AREA', 'geometry']]

# browse through unzipped files 
for tiff in glob.glob(tiff_fp):
    # read tiff file
    with rasterio.open(tiff) as src:
        array = src.read(1)
        affine = src.transform
    # compute zonal mean and get output as geojson
    zon_mean = zonal_stats(polys, array, affine=affine, stats='mean', all_touched=True, geojson_out=True)
    # turn geojson to GeoDataFrame
    temp = gpd.GeoDataFrame.from_features(zon_mean)    
    # create Year-month string for column name
    if char_string in tiff:
        yymm = tiff[-48:-42]
    else:
        yymm = tiff[-17:-11] # Late version in GPM data named differently, this should get the year from filename
    # rename columns
    temp = temp.rename(columns={'mean':yymm})
    # merge data to original polygon geodataframe
    polys = polys.merge(temp[['NAME', yymm]], on='NAME') 

# write updated polygon geodataframe to file
polys.to_file(out_fp, driver='ESRI Shapefile')













