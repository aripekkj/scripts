#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 22:13:27 2018


Script for renaming files in specified directory


@author: ari-pekkajokinen
14.2.2018
"""

import os
import glob

# set filepath
fp = r'/Volumes/SeagateExpansionDrive/Pictures/2018/Kilpisjarvi/Saittikuvat/'

# loop through the files and rename
os.chdir(fp)
for filename in glob.glob('*.JPG'):
    newname = filename[0:8] + '_apj' + '.JPG'
    os.rename(filename, newname)
    print(newname)
