#
#
# Join csv to geospatial data
#
# @ A-P Jokinen, 26.11.2019


# packages
library(sf)
library(dplyr)

# work dir
getwd()
setwd('E:/LocalData/aripekkj/TA/OpenStreetMap/madagascar-latest-free/')

# data
d <- read.csv('E:/LocalData/aripekkj/TA/Madagascar_city_populations.csv', sep = ";")

# check csv
head(d)

# rename columns
names(d)[names(d) == "Population.1.6.1975"] <- "pop_1975"
names(d)[names(d) == "Population.1.8.1993"] <- "pop_1993"
names(d)[names(d) == "Population.18.5.2018"] <- "pop_2018"

colnames(d)

# read shapefile
d_shape <- st_read('gis_osm_places_free_1.shp')

# check data
head(d_shape)

# join csv to shapefile
d_join <- left_join(d_shape, d, by = c("name" = "Name"))

# check result
head(d_join)
ncol(d_join)

# remove duplicates
d_join <- d_join[!duplicated(d_join$name), ]

# save the result
st_write(d_join, dsn = 'osm_places_w_population.shp', driver = 'ESRI Shapefile', delete_layer = TRUE)













