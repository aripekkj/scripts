## ---------------------------
##
## Purpose of script:
##
##  Reclassify raster based on given reclassify matrix
##
##
## Author: Ari-Pekka Jokinen
##
## Date Created: 2020-02-06
##
## Copyright (c) Ari-Pekka Jokinen, 2020
## Email: ari-pekka.jokinen@helsinki.fi
##
## ---------------------------
##
## Notes:
##   
##
## ---------------------------

library(raster)

# clear workspace
rm(list = ls())

# set workdir
getwd()
setwd("E:/LocalData/aripekkj/TA/Cambodia/Hansen/1.6")

# read file 
r <- raster("lossyear_merge_clip_above10.tif")

# define reclassification matrix, from, to new value
rcl.matrix <- c(0, 10, NA,
                10.1, 18, 1)

# reshape matrix to rows and columns
rcl.matrix <- matrix(rcl.matrix, ncol = 3, byrow = TRUE)

rcl.matrix

# reclassify
r.rcl <- reclassify(r, rcl.matrix)

plot(r.rcl)

# set filename for output
fname <- "loss_11_18.tif"

# write to file
writeRaster(r.rcl, filename = fname, format="GTiff")




