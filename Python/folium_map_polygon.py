# -*- coding: utf-8 -*-
"""
Created on Tue May 26 11:15:51 2020

@author: Ap
"""

import base64
import folium
import geopandas as gpd
from folium import IFrame
import glob
import os


# function to extract row by string
def getRowByString(String):
    row = fire.loc[fire['NAME'] == String]
    row_point = row.centroid
    return row_point;


# polygon filepath
fp = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\fire_count_pa_new.shp'
#fp = 'https://www.dropbox.com/s/wr59uzmu7nl5a3e/fire_count_pa.shp?dl=0'

# read file
firecount = gpd.read_file(fp)

# select only columns that are needed
fire = firecount[['WDPA_PID', 'NAME', 'diff20-19', 'geometry']]
fire['geo_id'] = fire.index.astype(str)

# map location
loc = -20.00, 47.00

# set path for glob to browse through files
img_path = r'C:\Users\Ap\Documents\ProtectedAreas\FireAlert\figures\*_n.png' # look only files that end with _s.png

# folium map
m = folium.Map(location=loc, zoom_start=7, tiles='Stamen Terrain')
#add polygons to map
folium.Choropleth(
    geo_data=fire,
    data=fire,
    columns=['geo_id', 'diff20-19'],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.5,
    legend_name='Difference in fires compared to the same period in 2019',
    #bins=bins,
    reset=True
).add_to(m)

# Convert polygon to GeoJson and add as a transparent layer to the map with tooltip
folium.features.GeoJson(fire,
                        name='Labels',
                        style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                        tooltip=folium.features.GeoJsonTooltip(fields=['NAME', 'diff20-19'],
                                                                aliases = ['Protected area', 'Difference in fires compared to 2019'],
                                                                labels=True,
                                                                sticky=False
                                                                            )
                       ).add_to(m)


html = '<div style="position: fixed; bottom: 100px; right: 50px; width: 300px; height: 120px; \
    background-color: #FFFFFF00; z-index:9000;"> \
        Data credit: \
        <br>NRT VIIRS 375 m Active Fire product VNP14IMGT. Available on-line \
        <br><a href="https://earthdata.nasa.gov/firms">https://earthdata.nasa.gov/firms</a> \
        <br><a href="https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/v1-vnp14imgt">DOI</a>\
        <br>UNEP-WCMC and IUCN (2020), Protected Planet: The World Database on Protected Areas (WDPA) \
        <br>Available at: <a href="https://www.protectedplanet.net">www.protectedplanet.net</a> \
        <br>Data visualization: Ari-Pekka Jokinen\
        </div>' 
m.get_root().html.add_child(folium.Element(html))



# browse through files in folder
for filename in glob.glob(img_path): 
    file_only = os.path.basename(filename[:-6]) # Get filename only to extract row
    img_fp = os.path.abspath(filename) # get full filepath to link image
    #print(file_only)
    #print(img_fp)
    marker_point = getRowByString(file_only) # use function to extract row and get point coordinates
    # open png image
    encoded = base64.b64encode(open(img_fp, 'rb').read())

    # add marker and png image as popup
    html = '<img src="data:image/png;base64,{}">'.format
    iframe = IFrame(html(encoded.decode('UTF-8')), width=620, height=420)
    popup = folium.Popup(iframe, max_width=650)
    
    icon = folium.Icon(color="red", icon="info-sign")
    marker = folium.Marker(location=[marker_point.y, marker_point.x],
                           popup=popup,
                           icon=icon)
    marker.add_to(m)
    

# save map
m.save("folium_map.html")








