#
#
#  This script reads files from a text file and masks each file by a mask layer
#
#

library(raster)
library(rgdal)

# set wd
getwd()
setwd("E:/LocalData/aripekkj/TA/Ghislain_Vieilledent_output_data/forest_cover")

# read mask layer
fc_latest <- raster("for2017.tif")

# read the text file containing raster files
f_txt <- read.table("listmyfolder.txt", header = FALSE, sep = "", stringsAsFactors = FALSE, fileEncoding = "UTF-16LE")

# Mask each file in the list with the mask layer in turn and save result. Mask outside of overlapping area
for (i in f_txt$V1){
  d <- raster(i)
  diff <- mask(d, fc_latest, inverse = TRUE)
  out_name <- paste(substr(i, 1, nchar(i)-4),tail(f_txt$V1,1), sep = "_")
  writeRaster(diff, filename = out_name, format = "GTiff")

}



#########
# another task: mask each raster from the earliest 
#########

# layer to be masked
fc_earliest <- raster("for2015.tif")

# read the text file containing raster files
f_txt <- read.table("listmyfolder.txt", header = FALSE, sep = "", stringsAsFactors = FALSE, fileEncoding = "UTF-16LE")

# Mask the earliest raster with each file in the list in turn and save result. Mask outside of overlapping area
for (i in f_txt$V1){
  d <- raster(i)
  diff <- mask(fc_earliest, d, inverse = TRUE)
  out_name <- paste("for2015", substr(i,1,nchar(i)-4), sep = "_")
  writeRaster(diff, filename = out_name, format = "GTiff")
  print(i)

}





