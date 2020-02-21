## ---------------------------
##
## Purpose of script: 
##
##    Create raster masks from GIMP land ice and ocean rasters
##    Mask digital elevation model with these rasters.
##    Mask DEM with RGI glacier extents.
##    write masked DEM to file
##
## Author: Ari-Pekka Jokinen
##
## Date Created: 2020-02-14
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
library(sf)

# set work dir
#getwd()
datadir <- "E:/LocalData/aripekkj/Greenland/"
setwd(datadir)

######### Creating land ice and ocean masks ###########

# list of land ice mask files
landice.list <- list.files("gimp/mask/land_ice/", full.names = TRUE)

# make land ice mask
landice.mask <- do.call(merge, lapply(landice.list, raster))

# list of ocean mask files
ocean.list <- list.files("gimp/mask/ocean/", full.names = TRUE)

# make ocean mask
ocean.mask <- do.call(merge, lapply(ocean.list, raster))

writeRaster(landice.mask, filename = "E:/LocalData/aripekkj/Greenland/GIMP/mask/landice_15.tif", format = "GTiff", datatype = "INT4U")
writeRaster(ocean.mask, filename = "E:/LocalData/aripekkj/Greenland/GIMP/mask/ocean_15.tif", format = "GTiff", datatype = "INT4U")


# 
landice <- raster("GIMP/mask/landice_15.tif")
ocean <- raster("GIMP/mask/ocean_15.tif")

# reproject to utm22N
ocean_utm22 <- projectRaster(ocean, res = 25, crs = "+proj=utm +zone=22 +datum=WGS84 +units=m +no_defs", method = 'bilinear')

landice_utm22 <- projectRaster(landice, res = 25, crs = "+proj=utm +zone=22 +datum=WGS84 +units=m +no_defs", method = 'bilinear')

writeRaster(landice_utm22, filename = "E:/LocalData/aripekkj/Greenland/GIMP/mask/landice_utm22n_25m.tif", format="GTiff", datatype="FLT4S")
writeRaster(ocean_utm22, filename = "E:/LocalData/aripekkj/Greenland/GIMP/mask/ocean_utm22n_25m.tif", format="GTiff", datatype="FLT4S")

########### MASK ###############

# set file path for raster to be masked
arcticdem <- raster("ArcticDEM/ArcticDEM_utm22_land.tif")
r.fp <- "E:/LocalData/aripekkj/Greenland/Aerodem/aerodem_1985_utm22_1.tif"
r <- raster(r.fp)

# reproject to utm22N
#r_utm22 <- projectRaster(r, res = 25, crs = "+proj=utm +zone=22 +datum=WGS84 +units=m +no_defs", method = 'bilinear')

# get

# read rgi shapefile
rgi_fp <- "E:/LocalData/aripekkj/Greenland/05_rgi60_Greenland_191107/05_rgi60_DiskoRegionUTM22_80s_extent.shp"
rgi <- st_read(rgi_fp)

# object as sp
rgi_sp <- as(rgi, "Spatial")

# set bounding box (UTM22N) and set it as extent
bbox <- extent(346000, 510000, 7680000, 8030000)

# crop all extents to bbox
landice_utm22_crop <- crop(landice_utm22, bbox)
ocean_utm22_crop <- crop(ocean_utm22, bbox)
r_crop <- crop(r, bbox)

# align the mask layers extent to dem extent
extent(landice_utm22_crop) <- alignExtent(bbox, r_crop, snap = 'near')   
extent(ocean_utm22_crop) <- alignExtent(bbox, r_crop, snap = 'near')
extent(r_crop) <- alignExtent(bbox, arcticdem, snap = 'near')

# mask out landice
r.m1 <- mask(r_crop, landice_utm22_crop, maskvalue=1)
# mask out ocean
r.m2 <- mask(r.m1, ocean_utm22_crop, maskvalue=1)
# mask also with rgi shapefile
r.masked <- mask(r.m2, rgi, inverse = TRUE)

# make a plot
par(mfrow=c(2,3), oma=c(1,1,3,1))
plot(landice_utm22_crop, main="Land ice mask")
plot(ocean_utm22_crop, main="Ocean mask")
plot(r_crop, main="DEM")
plot(r.m1, main="After land ice mask")
plot(r.m2, main="After land ice and ocean mask")
plot(r.masked, main="After land ice, ocean and \n RGI polygon mask")
mtext("Masking process", outer = TRUE)

########### WRITE OUTPUT ###############

writeRaster(r.masked, filename = "E:/LocalData/aripekkj/Greenland/Aerodem/aerodem_1985_utm22_land.tif", format="GTiff", datatype="FLT4S")

