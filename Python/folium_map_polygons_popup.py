# -*- coding: utf-8 -*-
"""
Created on Tue May 26 11:15:51 2020

Create a folium map with popup images


Updates:
    Added MarkerCluster class with popups 15.6.2020

@author: Ap
"""

import base64
import folium
import pandas as pd
import geopandas as gpd
from folium import IFrame
from folium.plugins import MarkerCluster
import glob
import os
import numpy as np

# function to extract row by string
def getPointByString(String):
    row = fire.loc[fire['NAME'] == String]
    row_point = row.centroid
    return [row, row_point];
    
# polygon filepath
fp = r'C:\Users\Ap\Documents\ProtectedAreas\Madagascar\WDPA\WDPA_VIIRSfire_sums_mar_jun_1520.shp'


# read file
firecount = gpd.read_file(fp)

# select only columns that are needed
fire = firecount[['WDPA_PID', 'NAME', 'diff_2020_', 'cat', 'geometry']]
fire['geo_id'] = fire.index.astype(str)
# create columns for x and y coordinates
fire['x'] = fire.geometry.centroid.x
fire['y'] = fire.geometry.centroid.y

# map location
loc = -20.00, 47.00

# set path for glob to browse through files
img_path = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\figures\Madagascar\*.png' # look only files that end with _s.png

# set categories for choropleth map legend
#bins = list([0, 25, 50, max(fire['diff20-19'])]) # not working

# folium map
m = folium.Map(location=loc, zoom_start=7, tiles='Stamen Terrain')


#add polygons to map
folium.Choropleth(
    geo_data=fire,
    data=fire,
    columns=['geo_id', 'cat'],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.5,
    legend_name='-1: less fires in 2020, 1: more fires in 2020',
    bins=4,
    reset=True
).add_to(m)


# Convert polygon to GeoJson and add as a transparent layer to the map with tooltip
folium.features.GeoJson(fire,
                        name='Labels',
                        style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                        tooltip=folium.features.GeoJsonTooltip(fields=['NAME', 'diff_2020_'],
                                                                aliases = ['Protected area', 'Difference in 2020 fires compared to average from 2015-2019'],
                                                                labels=True,
                                                                sticky=False
                                                                            )
                       ).add_to(m)


html = '<div style="position: fixed; bottom: 30px; right: 5px; width: 200px; height: 60px; \
    background-color: #FFFFFF00; z-index:9000; line-height: 10px"> \
        <font size="1">\
        Data: \
        <br>VIIRS Active Fire product \
        <br><a href="https://earthdata.nasa.gov/firms">https://earthdata.nasa.gov/firms</a> \
        <a href="https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/v1-vnp14imgt">DOI</a>\
        <br>UNEP-WCMC and IUCN (2020) \
        <br><a href="https://www.protectedplanet.net">www.protectedplanet.net</a> \
        <br>Data visualization: Ari-Pekka Jokinen\
        </font>\
        </div>' 
m.get_root().html.add_child(folium.Element(html))

# empty geodataframe for point coordinate rows
point_coords = gpd.GeoDataFrame()
# empty lists to store objects
popuplist = []
iconlist = []
# browse through files in folder
for filename in glob.glob(img_path): 
    file_only = os.path.basename(filename[:-4]) # Get filename only to extract row
    img_fp = os.path.abspath(filename) # get full filepath to link image
    
    result = getPointByString(file_only) # use function to extract row and get point coordinates
    marker_row = result[0]
    marker_point = result[1]
    
    # add row to dataframe
    point_coords = point_coords.append(marker_row)
    
    # open png image
    encoded = base64.b64encode(open(img_fp, 'rb').read())

    # add marker and png image as popup
    html = '<img src="data:image/png;base64,{}">'.format
    iframe = IFrame(html(encoded.decode('UTF-8')), width=620, height=420)
    popup = folium.Popup(iframe, max_width= 600)
    popuplist.append(popup)
    icon = folium.Icon(color="red", icon="info-sign")
    iconlist.append(icon)
    # simple marker
    #marker = folium.Marker(location=[marker_point.y, marker_point.x],
    #                       popup=popup,
    #                       icon=icon) # 
    #marker.add_to(m)
    

# create a list of coordinates from extracted rows
locations = list(zip(point_coords["y"], point_coords["x"]))

# create marker_cluster class and add it to map
marker_cluster = MarkerCluster(locations, popups=popuplist, icons=iconlist)
m.add_child(marker_cluster)

# save map
m.save("folium_map_2508.html")








