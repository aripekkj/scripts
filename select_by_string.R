# select rows from file by matching string
# 
# Script contains workflow for csv and shapefile
# 1st CSV
# 2nd Shapefile
#
#
#
# @ A-P Jokinen, 26.11.2019



# packages
library(sf)
library(plyr)
library(rgdal)


# workdir
getwd()
setwd('E:/LocalData/aripekkj/TA/OpenStreetMap/madagascar-latest-free/')
#setwd('E:/LocalData/aripekkj/TA/WDPA_Oct2019_MDG-shapefile/')
#setwd('E:/LocalData/aripekkj/R/')


################ WITH CSV FILE #####################

# read csv
d <- read.csv('osm_roads.csv', sep=';')

# check data
head(d)
cnames <- colnames(d)

# select by string
strings <- c("primary","primary_link","secondary","secondary_link","tertiary","tertiary_link","track","unclassified")

result <- data.frame()

# make a selection by string in strings and finally rbind all selections to dataframe "result"
for (string in strings) {
  # make selection acccording to "string" from dataframe d
  s1 <- d[d$fclass== string,]
  # bind the results to dataframe
  result <- rbind(result, s1)
}  

# check results
head(result)
unique(result$fclass)

# save as csv
write.csv(result, file = "selected_roads.csv", sep = ";")


#############  SAME WITH SHAPEFILE #################

# read shapefile using sf package
d_sf <- st_read('gis_osm_roads_free_1.shp')

# select by string (exact match)
strings <- c("primary","primary_link","secondary","secondary_link","tertiary","tertiary_link","track","unclassified")


# empty data frame for selections
result <- data.frame()

# make a selection by string in strings and finally rbind all selections to dataframe "result"
for (string in strings) {
  # make selection acccording to "string" from dataframe d
  s1 <- d_sf[d_sf$fclass== string,]
  # bind the results to dataframe
  result <- rbind.data.frame(result, s1)
}  

# check results
head(result)
unique(result$fclass)

# write to file
st_write(result, dsn = 'osm_roads_pri_sec_ter_unc_tra.shp', driver = 'ESRI Shapefile')




