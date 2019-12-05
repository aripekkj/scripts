#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 12:40:06 2018

Script for finding image names matching with the image numbers from flight lines


@author: ari-pekkajokinen
"""

# import modules
import pandas as pd
import numpy as np
import os
import glob

# set filepaths and read data
fp = r'/Volumes/SeagateExpansionDrive/GreenlandAerialPhotos/nuussuaq_flight_lines_fn_uppercase_change_strip.csv'
flight_lines = pd.read_csv(fp, sep=';')
image_fp = r'/Volumes/SeagateExpansionDrive/GreenlandAerialPhotos/nuussuaq_50k/'
image_names = r'/Volumes/SeagateExpansionDrive/GreenlandAerialPhotos/list_nussuaq.txt'
images = pd.read_csv(image_names)

# Save image list as csv
images_outfp = r'/Volumes/SeagateExpansionDrive/GreenlandAerialPhotos/list_nuussuaq_2.csv'
images.to_csv(images_outfp)

# check data
print(flight_lines.head(15))
print(images.head(5))


"""
Here image numbers are changed to three digit format. For example a value of 1 in 
'image' column is formatted to 001. Additionally null values are removed from the 
DataFrame. The values are handled as strings because some fields may contain not only numbers
"""
# Create empty DataFrame for testing
test_asdf = pd.DataFrame()

# Copy values from 'image' column in flight lines DataFrame to test DataFrame
test_asdf['image'] = flight_lines['image']

# Here is an example showing what zfill does
test_asdf['image'][20].zfill(3)

# Before beginning, let's check if there are null values in the data
flight_lines['image'].isnull().sum()

# Find null values and extract indices to a list
flight_lines[flight_lines['image'].isnull()].index.tolist()

# Drop null value rows from DataFrame
flight_lines = flight_lines.dropna(axis=0, subset=['image'])

# Create empty list for 3 digit values
threeDigit = []

# loop over the image number column and change the numbers to three digit format
for n in flight_lines['image']:
    # Assign the number 3 digit long
    new_number = n.zfill(3)
    # Add 3 digit number to a list
    threeDigit.append(new_number)
    print(n)
    break

# List values as Series
threeDigitSeries = pd.Series(threeDigit)

# Create new column from the list values
flight_lines['threeDigit'] = threeDigitSeries.values

# Check data
print(flight_lines.head(20))




"""
Parsing the image filenames and matching the flight line data to the images
"""

# Create empty column for flight line filenames
flight_lines['filename'] = flight_lines['project'] + '_' + flight_lines['strip'] + '_' + flight_lines['threeDigit']

print(flight_lines['filename'])

# Change the column values as string
flight_lines['filename'] = flight_lines['filename'].astype(str)

# Empty dataframe for the filename and flight line matches
#image_places = pd.DataFrame()
test = []
# Set directory where to search for image files
os.chdir(image_fp)
# match filenames with the 'project', 'strip' and 'field' columns in flight_lines
for filename in glob.glob('*.tif'):
    asdf = flight_lines.loc[flight_lines['filename'] == filename[:-4]]
    #data = asdf.to_dict()
    test.append(asdf)

df = pd.concat(test)

# save as csv
outfp = r'/Volumes/SeagateExpansionDrive/GreenlandAerialPhotos/image_matches_new.csv'
df.to_csv(outfp, sep=';')














""" From here these are different ways to try selecting the mathcing values
    and the scripts are not complete

# Use text file with image filenames to select certain rows from flight lines
for i in flight_lines['filename']:
    print(i)
    for j in images:
        print(j)
        if j in i:
            print('ulaulaulaulaulaula')
        asdf = flight_lines.loc[flight_lines['filename'] == images[:-4]]



# find filenames from the directory and compare to the flight lines
for filename in glob.glob('*.tif'):
    for i in flight_lines['filename']:
        # If a match is found, add the row from flight line to a new dataframe
        if i in filename:
            
            print(i)    
    
"""





