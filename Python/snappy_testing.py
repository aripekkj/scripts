# -*- coding: utf-8 -*-
"""
Spyder Editor

ESA SNAP API for Python (snappy) testing 



"""

from snappy import ProductIO
import matplotlib.pyplot as plt
import numpy as np

# read .dim file
p = ProductIO.readProduct('C:/Users/Ap/anaconda3/envs/snappy36/snappy/testdata/MER_FRS_L1B_SUBSET.dim')
list(p.getBandNames())

# assign one band to a variable
band = p.getBand('radiance_1')
# get band width and height
w = p.getSceneRasterWidth()
h = p.getSceneRasterHeight()

# create an empty array
band_data = np.zeros(w*h, np.float32)

# populate array with band values
band.readPixels(0,0,w,h, band_data)

# reshape
band_data.shape = h,w

# plot data
plt.figure(figsize=(18,10))
plt.imshow(band_data, cmap=plt.cm.binary)
plt.show()





