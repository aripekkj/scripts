##
##  Calculate slope
## 

library(raster)
library(rgdal)

# working directory
getwd()
setwd("E:/LocalData/aripekkj/TA/Bhutan/Bhutan_SRTM30")

# read data
dem <- raster('srtm30m_merge_clip.tif')

# calculate slope in degrees and radians, and aspect
slope <- terrain(dem, opt="slope", unit="degrees", neighbors=8, filename="SRTM30_slope_deg")
slope_rd <- terrain(dem, opt="slope", unit="radians", neighbors=8, filename="SRTM30_slope_rd")
aspect <- terrain(dem, opt="aspect", unit="radians", filename = "SRTM30_aspect")

# hillshade
hs <- hillShade(slope_rd, aspect, angle = 45, direction = 315, filename = "SRTM30_hillshade")

# write to file
writeRaster(hs, filename = "SRTM30_hillshade", format = "GTiff")
writeRaster(slope, filename = "SRTM30_slope_deg", format = "GTiff")






