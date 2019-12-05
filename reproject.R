#
#
# Reproject rasters
#
#
# Ap Jokinen, 29.11.2019


# packages
library(raster)
library(rgdal)

# work dir
getwd()
setwd("E:/LocalData/aripekkj/Greenland/Kortforsyning_download/Orthophoto/")

# read filelist
f_list <- read.table("filelist.txt", header = FALSE, stringsAsFactors = FALSE, fileEncoding = "UTF-16LE")

# check
head(f_list)

# proj4 details for utm35
utm22n <- "+proj=utm +zone=22 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

# suffix
suf <- "_utm22N"

# reproject
for (i in f_list$V1){
  # read file from list as a raster stack
  f <- raster(i)
  # reproject file
  reprojected <- projectRaster(f, crs = utm22n)
  #output filename
  out_name <- paste(substr(i, 1, nchar(i)-4), suf, sep = "")
  # write file to folder
  writeRaster(reprojected, filename = out_name, format = "GTiff")
  break
}
