
library(tidyverse)
library(dplyr)
library(raster)
library(sf)
library(rgdal)
library(ggplot2)
library(lubridate)
library(readr)

fp = 'D://Users//E1008409//MK//Ruovikko//Velmu-aineisto//combined.velmu.aland.data.11.05.2021.csv'
fp_r = 'D://Users//E1008409//MK//Ruovikko//ruovikko_binary_201907_ver2.tif'
fp_bayes = 'D://Users//E1008409//MK//Ruovikko//bayes_ruovikko_201907.tif'

# read data
d <- read.csv(fp, sep=';', header=TRUE)
r <- raster::stack(fp_r)
# stack both rasters
r.bayes <- raster::stack(fp_r, fp_bayes)

# get some of the first columns
head(colnames(d), 60)


# select phragmites_australis
ds <- dplyr::select(d, c('pvm', 'sykeid', 'n_euref', 'e_euref', 'menetelma', 'syvyys_mitattu','Phragmites_australis')) # Schoenoplectus_sp, Typha_sp

# create date column
ds$date <- as.Date(as.character(ds$pvm), format = '%d.%m.%Y')
ds$syvyys_mitattu <- as.numeric(gsub(",", ".", gsub("\\.", "", ds$syvyys_mitattu)))

# selection
#start <- '2019-07-01'
#end <- '2019-07-31'
#dsel <- with(ds, ds[(date >= start & date <= end), ])

# select july and august 2019 and 2020
dsel <- ds %>%
  filter(day(date) >= 1 & month(date) == 07 & year(date) == 2019 |
        day(date) >= 1 & month(date) == 07 & year(date) == 2020 |   
        day(date) >= 1 & month(date) == 08 & year(date) == 2019 |
        day(date) >= 1 & month(date) == 08 & year(date) == 2020 )
#        day(date) >= 1 & month(date) == 07 & year(date) == 2018 |
#        day(date) >= 1 & month(date) == 08 & year(date) == 2018 |
#        day(date) >= 1 & month(date) == 07 & year(date) == 2017 |
#       day(date) >= 1 & month(date) == 08 & year(date) == 2017 |
 #       day(date) >= 1 & month(date) == 07 & year(date) == 2016 |
#        day(date) >= 1 & month(date) == 08 & year(date) == 2016         )

# reformat commas to dots
dsel$northing <- as.numeric(gsub(",", ".", dsel$n_euref))
dsel$easting <- as.numeric(gsub(",", ".", dsel$e_euref))
#str(dsel)

# make a spatial point layer
coordsys <- r@crs # from raster layer
dspat <- SpatialPointsDataFrame(dsel[,c('easting', 'northing')], dsel, proj4string = coordsys)


dspat$syvyys_mitattu[is.na(dspat$syvyys_mitattu)] <- -9999
# select rows where 'menetelma' != 21 or 42 <- (lot of off shore obs)
dspat <- dspat[dspat$menetelma != 21, ]
dspat <- dspat[dspat$menetelma != 44, ]
dspat <- dspat[dspat$menetelma != 42, ]
#dspat <- dspat[dspat$syvyys_mitattu >= -1.5, ]
#dspat <- subset(dspat, menetelma != 21 | menetelma != 42)
test <- dspat[dspat$menetelma != 44, ]
############################################
##### Extracting values from exact point ###
############################################
# extract raster value from points
ext <- raster::extract(r.bayes, dspat, method = 'simple', df=TRUE)

# add plot id
ext$syke_id <- dspat$sykeid

# merge to other data
merged <- merge(dspat, ext, by.x='sykeid', by.y='syke_id')
#head(merged,20)

# replace NAs in ruovikko column
merged$ruovikko_binary_201907_ver2[is.na(merged$ruovikko_binary_201907_ver2)] <- 9999

# write merged to shapefile
#writeOGR(merged, "D://Users//E1008409//MK//Ruovikko", "Phragmites_sampled_ex21_07081920", driver = "ESRI Shapefile", overwrite_layer = TRUE)

# rename column in merged
names(merged)[names(merged) == 'ruovikko_binary_201907_ver2'] <- "rbin_pts201907"
names(merged)[names(merged) == 'bayes_ruovikko_201907'] <- "rbay_pts201907"
# as 'normal' dataframe
ruovikkoTrue <- as.data.frame(merged)

# column values to numeric
ruovikkoTrue$Phragmites_australis <- as.numeric(gsub(",", ".", ruovikkoTrue$Phragmites_australis))

################################
### Presence absence plot ######
################################

# modify coverage to presence absence
dpres <- ruovikkoTrue
dpres$Phragmites_australis[dpres$Phragmites_australis > 0] <- 1
unique(dpres$Phragmites_australis) # check

# select where ruovikko product = True
#dpres <- dpres[dpres$ruovikko_binary_201907_ver2 == 1, ]

# group and count
t <- dpres %>%
  group_by(Phragmites_australis, rbin_pts201907) %>%
  summarise(count=n())

# drop row 0 9999
#t <- t[-c(3),]

# add descriptive column
t$Categories <- c('Not observed,\n not predicted', 'Not observed,\n predicted', 'Not observed,\n NA', 'Observed,\n Not predicted', 'Observed,\n Predicted', 'Observed,\n NA')

# plot
b <- barplot(t$count, names.arg=t$Categories, ylim=c(0, max(t$count)+1000), 
             main=paste('Comparison to VELMU Phragmites australis \n exact point observations from July and August 2019-2020'),
             ylab='Count')
text(b, t$count+300, t$count)

# logical test
t$class <- t$Phragmites_australis == t$rbin_pts201907 | t$rbin_pts201907 == 9999

# category names
t$class[t$class == TRUE] <- 'Correct'
t$class[t$class == FALSE] <- 'Incorrect'
t$class[t$rbin_pts201907 == 9999] <- 'NA'

# compute percentage of counts
t$prcnt <- round(t$count / sum(t$count), 3)


ggplot(t, aes(fill=Categories, y=prcnt, x=class,)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(label=paste0(prcnt*100,"%")), position = position_stack(vjust = 0.5), size = 3) +
  scale_y_continuous(labels = scales::percent) +
  labs(x = "", y = "Percent", title = "Correct and incorrect values in the reeds product \n based on exact point extraction")
  
#t.phragaus1 <- t[t$Phragmites_australis == 1, ]
# plot
#bt <- barplot(t.phragaus1$count, names.arg=t.phragaus1$text, ylim=c(0, max(t.phragaus1$count)+50), 
#             main=paste('Validation against VELMU Phragmites australis \n observations from July and August 2019-2020'),
#             ylab='Count')
#text(bt, t.phragaus$count+10, t.phragaus1$count)

###################################################
################ Buffered analysis ################
###################################################


# loop for multiple buffers
#buffers <- c(20, 50)

#for ( i in buffers){
#  ext.pts <- ext.buf <- raster::extract(r, dspat, df=TRUE, weights=TRUE, buffer = i, fun = 'mean') # slow
  # rename column
#  bufstring <- paste0("rvkbin_", i,"_201907")
#  names(ext.pts)[names(ext.pts) == "ruovikko_binary_201907_ver2"] <- bufstring

  # add plot id
#  ext.pts$syke_id <- dspat$sykeid
  
  # merge to other data
#  merged <- merge(merged, ext.pts, by.x='sykeid', by.y='syke_id')
  
#  print(paste0('Done with buffer ', i))
#  }


# set buffer
buffer <- 20

# extract cell values to points
ext.buf <- raster::extract(r.bayes, dspat, df=TRUE, weights=TRUE, buffer = buffer, fun = 'mean') # slow

# add plot id
ext.buf$syke_id <- dspat$sykeid

# merge to other data
merged.buf <- merge(merged, ext.buf, by.x='sykeid', by.y='syke_id')

# replace NAs in ruovikko column
merged.buf$ruovikko_binary_201907_ver2[is.na(merged.buf$ruovikko_binary_201907_ver2)] <- 9999
# as 'normal' dataframe
ruovikkoTrue.buf <- as.data.frame(merged.buf)

# column values to numeric
ruovikkoTrue.buf$Phragmites_australis <- as.numeric(gsub(",", ".", ruovikkoTrue.buf$Phragmites_australis))


# save with all point samplings
#writeOGR(merged.buf, "D://Users//E1008409//MK//Ruovikko", "Phragmites_all_sampled_ex2142_07081920", driver = "ESRI Shapefile", overwrite_layer = TRUE)

# read shapefile
shape <- readOGR("D://Users//E1008409//MK//Ruovikko//Phragmites_all_sampled_ex2142_07081920.shp")

# as normal dataframe
shape.df <- as.data.frame(shape)
# rename columns
names(shape.df)[names(shape.df) == 'r__2019'] <- 'ruovikko_binary_201907_ver2'
names(shape.df)[names(shape.df) == 'b__2019'] <- 'bayes_ruovikko_201907'
names(shape.df)[names(shape.df) == 'Phrgmt_'] <- 'Phragmites_australis'


####################################################
### Presence absence plot for buffered points ######
####################################################

# modify coverage to presence absence
dpres.buf <- shape.df #ruovikkoTrue.buf
dpres.buf$Phragmites_australis[dpres.buf$Phragmites_australis > 0] <- 1
# thresholding
dpres.buf$ruovikko_binary_201907_ver2[dpres.buf$ruovikko_binary_201907_ver2 > 0 & dpres.buf$ruovikko_binary_201907_ver2 <= 1] <- 1
dpres.buf$ruovikko_binary_201907_ver2[dpres.buf$ruovikko_binary_201907_ver2 < 0.25] <- 0

unique(dpres.buf$Phragmites_australis) # check
unique(dpres.buf$ruovikko_binary_201907_ver2) # check

# select where ruovikko product = True
#dpres <- dpres[dpres$ruovikko_binary_201907_ver2 == 1, ]

# group and count
t.buf <- dpres.buf %>%
  group_by(Phragmites_australis, ruovikko_binary_201907_ver2) %>%
  summarise(count=n())

# drop row 0 9999
#t.buf <- t.buf[-c(3),]

# add descriptive column
t.buf$Categories <- c('Not observed,\n not predicted', 'Not observed,\n predicted', 'Not observed,\n NA', 'Observed,\n Not predicted', 'Observed,\n Predicted', 'Observed,\n NA')

# plot
#png(filename = paste("D://Users//E1008409//MK//Ruovikko//kuvat ja plotit//", "valid_", buffer, "_m_buffer_", start, "_", end, ".png", sep = ""))
b.buf <- barplot(t.buf$count, names.arg=t$Categories, ylim=c(0, max(t.buf$count)+1000), 
             main=paste('Comparison to VELMU Phragmites australis on \n', buffer, 'm buffered observations from July and August 2019-2020'),
             ylab='Count')
text(b.buf, t.buf$count+300, t.buf$count)
#dev.off()
# and extracted reeds presence > 25% \n

# logical test
t.buf$class <- t.buf$Phragmites_australis == t.buf$ruovikko_binary_201907_ver2 | t.buf$ruovikko_binary_201907_ver2 == 9999

# category names
t.buf$class[t$class == TRUE] <- 'Correct'
t.buf$class[t$class == FALSE] <- 'Incorrect'
t.buf$class[t$rbin_pts201907 == 9999] <- 'NA'

# compute percentage of counts
t.buf$prcnt <- round(t.buf$count / sum(t.buf$count), 3)


ggplot(t.buf, aes(fill=Categories, y=prcnt, x=class,)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(label=paste0(prcnt*100,"%")), position = position_stack(vjust = 0.5), size = 3) +
  scale_y_continuous(labels = scales::percent) +
  labs(x = "", y = "Percent", title = paste0("Correct and incorrect values in the reeds product \n based on ", buffer," m buffered point locations")) # \n and > 25% extracted reeds presence"))




############################################################
################ Buffered analysis to Bayes reeds ################
############################################################
merged.buf <- shape

# rename columns
names(merged.buf)[names(merged.buf) == 'r__2019'] <- 'ruovikko_binary_201907_ver2'
names(merged.buf)[names(merged.buf) == 'b__2019'] <- 'bayes_ruovikko_201907'
names(merged.buf)[names(merged.buf) == 'Phrgmt_'] <- 'Phragmites_australis'

boxplot(merged.buf$rbay_pts201907)

plot(merged.buf$bayes_ruovikko_201907, merged.buf$Phragmites_australis)

Q <- quantile(merged.buf$bayes_ruovikko_201907, probs=c(.25, .75), na.rm = TRUE)
iqr <- IQR(merged.buf$bayes_ruovikko_201907, na.rm=TRUE)

up <-  Q[2]+1.5*iqr # Upper Range  
low<- Q[1]-1.5*iqr # Lower Range

eliminated<- subset(merged.buf, merged.buf$bayes_ruovikko_201907 > (Q[1] - 1.5*iqr) & merged.buf$bayes_ruovikko_201907 < (Q[2]+1.5*iqr))

seltest <- eliminated[eliminated$Phragmites_australis > 0 , ]

plot(seltest$bayes_ruovikko_201907, seltest$Phragmites_australis)

# as 'normal' dataframe
rbay.buf <- as.data.frame(merged.buf)

# column values to numeric
rbay.buf$Phragmites_australis <- as.numeric(gsub(",", ".", rbay.buf$Phragmites_australis))

# drop na 
rbay.buf <- rbay.buf[is.na(rbay.buf$bayes_ruovikko_201907) == FALSE, ]
rbay.buf <- rbay.buf[rbay.buf$bayes_ruovikko_201907 < 5000, ] # drop few outliers

# test subset 
rbay.buf <- subset(rbay.buf, Phragmites_australis > 50 ) #  Phragmites_australis == 0 |

# new col
rbay.buf$phragausbin <- rbay.buf$Phragmites_australis
rbay.buf$phragausbin[rbay.buf$phragausbin > 0] <- 1

# groupby Phragmites australis coverage and compute mean for each coverage from bayes mean
#tapply(rbay.buf$bayes_ruovikko_201907, rbay.buf$phragausbin, mean)

# conditional plot
rbay.buf$phragausbin <- as.factor(rbay.buf$phragausbin)
par(mar = c(5,4,4,4) + 0.1)
cdplot(rbay.buf$phragausbin ~ rbay.buf$bayes_ruovikko_201907,
       main = "Reeds presence/absence predicted by Bayes reeds product",
       xlab = "Bayes reeds product probability density",
       ylab = "Phragmites australis presence (1) and absence (0)")
mtext("Proportion", side=4, line=3)

plot(rbay.buf$bayes_ruovikko_201907, rbay.buf$Phragmites_australis,
     xlab='Bayes probability density', ylab='Phragmites australis coverage',
     main = "Phragmites australis coverage against Bayes reeds probability density")
cortext <- round(cor(rbay.buf$bayes_ruovikko_201907, rbay.buf$Phragmites_australis),3)
text(50, 100, paste0("cor: ", cortext))


#
rtest <- rbay.buf[is.na(rbay.buf$bayes_ruovikko_201907) == FALSE, ]
rtest <- rtest[rtest$bayes_ruovikko_201907 < 5000, ]

plot(rtest$bayes_ruovikko_201907, rtest$Phragmites_australis, xlab='Bayes probability density', ylab='Phragmites australis coverage')
cortext <- round(cor(rtest$bayes_ruovikko_201907, rtest$Phragmites_australis),3)
text(50, 100, paste0("cor: ", cortext))
#

rpres <- rtest[rtest$Phragmites_australis > 0, ]
plot(rpres$bayes_ruovikko_201907, rpres$Phragmites_australis, xlab='Bayes probability density', ylab='Phragmites australis coverage')
cortext <- round(cor(rpres$bayes_ruovikko_201907, rpres$Phragmites_australis),3)
text(50, 100, paste0("cor: ", cortext))


#



# testing
orig_len = length(dspat)
res.list = list()
run.buffer = 5

while (length(dspat) > 10){
  test.buf <- raster::extract(r, dspat, df=TRUE, weights=TRUE, buffer = run.buffer, fun = 'mean')
  # add plot id
  test.buf$syke_id <- dspat$sykeid
  
  # merge to other data
  dspat <- merge(dspat, test.buf, by.x='sykeid', by.y='syke_id')
  # select
  dspat <- subset(dspat, ruovikko_binary_201907_ver2 == 1,)
  
  # row length
  row.len <- length(dspat)
  print(paste0(round(length(dspat)/orig_len*100, 2), "% of the  points remaining after buffer ", run.buffer))
  run.buffer <- run.buffer + 5    
  
  # append numberof rows to list
  res.list <- append(res.list, row.len)
  # remove sampled points column
  dspat$ruovikko_binary_201907_ver2 <- NULL
  dspat$ruovikko_binary_201907_ver2.y <- NULL
  dspat$ruovikko_binary_201907_ver2.x <- NULL
  
  }



####################################################
### Presence absence plot for buffered points ######
####################################################

plot(ruovikkoTrueb.buf$bayes_ruovikko_201907, ruovikkoTrueb.buf$Phragmites_australis)

# modify coverage to presence absence
dpresb.buf <- ruovikkoTrueb.buf
dpresb.buf$Phragmites_australis[dpres.buf$Phragmites_australis > 0] <- 1
dpresb.buf$ruovikko_binary_201907_ver2[dpres.buf$ruovikko_binary_201907_ver2 >= 0.25 & dpres.buf$ruovikko_binary_201907_ver2 <= 1] <- 1
unique(dpres.buf$Phragmites_australis) # check
unique(dpres.buf$ruovikko_binary_201907_ver2) # check

# select where ruovikko product = True
#dpres <- dpres[dpres$ruovikko_binary_201907_ver2 == 1, ]

# group and count
t.buf <- dpres.buf %>%
  group_by(Phragmites_australis, ruovikko_binary_201907_ver2) %>%
  summarise(count=n())

# drop row 0 9999
#t.buf <- t.buf[-c(3),]

# add descriptive column
t.buf$text <- c('Not observed,\n not predicted', 'Not observed,\n predicted', 'Not observed,\n NA', 'Observed,\n Not predicted', 'Observed,\n Predicted', 'Observed,\n NA')

# plot
#png(filename = paste("D://Users//E1008409//MK//Ruovikko//kuvat ja plotit//", "valid_", buffer, "_m_buffer_", start, "_", end, ".png", sep = ""))
b.buf <- barplot(t.buf$count, names.arg=t$text, ylim=c(0, max(t.buf$count)+1000), 
                 main=paste('Comparison to VELMU Phragmites australis on \n', buffer, 'm buffered observations from July and August 2019-2020'),
                 ylab='Count')
text(b.buf, t.buf$count+300, t.buf$count)
#dev.off()

# logical test
t.buf$class <- t.buf$Phragmites_australis == t.buf$ruovikko_binary_201907_ver2

# compute percentage of counts
t.buf$prcnt <- round(t.buf$count / sum(t.buf$count), 3)


ggplot(t.buf, aes(fill=text, y=prcnt, x=class,)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(label=paste0(prcnt*100,"%")), position = position_stack(vjust = 0.5), size = 3) +
  scale_y_continuous(labels = scales::percent) +
  labs(x = "", y = "Percent", title = paste0("Correct and incorrect values in the reeds product \n based on ", buffer," m buffered point locations"))




#####################################3
### Previous data browsing #########
#######################################

# select rows where ruovikko is 1
ruovikko1 <- ruovikkoTrue[ruovikkoTrue$ruovikko_binary_201907_ver2 == 1, ]
str(ruovikko1)

# count occurrences
ruovikko_counts <- ruovikko1 %>%
  group_by(Phragmites_australis) %>%
  summarise(count=n())

# get some numbers
zeros <- sum(ruovikko_counts$count[1])
not_zeros <- sum (ruovikko_counts$count[2:length(ruovikko_counts$count)])
# count where Phrag. australis > 5 and 25
phragaus5 <- ruovikko_counts[ruovikko_counts$Phragmites_australis >= 5, ]
phrag5_count <- sum(phragaus5$count)

phragaus25 <- ruovikko_counts[ruovikko_counts$Phragmites_australis >= 25, ]
phrag25_count <- sum(phragaus25$count)

# plot
xmax = max(ruovikko_counts$Phragmites_australis)
ymax = max(ruovikko_counts$count)

png(filename = "D://Users//E1008409//MK//Ruovikko//kuvat ja plotit//velmu_pts.july.png")
barplot(ruovikko_counts$count, names.arg=unique(ruovikko_counts$Phragmites_australis),
        main='Reeds product presence comparison to VELMU species data \n at exact point locations',
        xlab=paste('Phragmites australis presence (0-100) in ' , start , '-' , end),
        ylab='Number of observations')
text(10, ymax-5, paste('0 values: ', round(zeros/sum(ruovikko_counts$count)*100, 2), '%'))
text(10, ymax-10, paste('Other than 0 values: ', round(not_zeros/sum(ruovikko_counts$count)*100, 2), '%'))
text(10, ymax-15, paste('Above 5 values: ', round(phrag5_count/sum(ruovikko_counts$count)*100, 2), '%'))
text(10, ymax-20, paste('Above 25 values: ', round(phrag25_count/sum(ruovikko_counts$count)*100, 2), '%'))
text(10, ymax-25, paste('Total points: ', length(ruovikko1$ruovikko_binary_201907_ver2)))
dev.off()



###########33 Buffered points ##########3

# select rows where ruovikko is 1
ruovikko1.buf <- ruovikkoTrue.buf[ruovikkoTrue.buf$ruovikko_binary_201907_ver2 > 0 & ruovikkoTrue.buf$ruovikko_binary_201907_ver2 < 2, ]
str(ruovikko1.buf)

# count occurrences
ruovikko_counts.buf <- ruovikko1.buf %>%
  group_by(Phragmites_australis) %>%
  summarise(count=n())

# get some numbers
zeros.buf <- sum(ruovikko_counts.buf$count[1])
not_zeros.buf <- sum (ruovikko_counts.buf$count[2:length(ruovikko_counts.buf$count)])
# count where Phrag. australis > 5 and 25
phragaus5.buf <- ruovikko_counts.buf[ruovikko_counts.buf$Phragmites_australis >= 5, ]
phrag5.buf_count <- sum(phragaus5.buf$count)

phragaus25.buf <- ruovikko_counts.buf[ruovikko_counts.buf$Phragmites_australis >= 25, ]
phrag25.buf_count <- sum(phragaus25.buf$count)

# plot
xmax.buf = max(ruovikko_counts.buf$Phragmites_australis)
ymax.buf = max(ruovikko_counts.buf$count)

barplot(ruovikko_counts.buf$count, names.arg=unique(ruovikko_counts.buf$Phragmites_australis),
        main='Reeds presence comparison to VELMU species data \n with 10m buffer in point locations',
        xlab=paste('Phragmites australis presence (0-100) in ' , start , '-' , end),
        ylab='Number of observations')
text(20, ymax.buf-5, paste('0 values: ', round(zeros.buf/sum(ruovikko_counts.buf$count)*100, 2), '%'))
text(20, ymax.buf-20, paste('Other than 0 values: ', round(not_zeros.buf/sum(ruovikko_counts.buf$count)*100, 2), '%'))
text(20, ymax.buf-35, paste('Above 5 values: ', round(phrag5.buf_count/sum(ruovikko_counts.buf$count)*100, 2), '%'))
text(20, ymax.buf-50, paste('Above 25 values: ', round(phrag25.buf_count/sum(ruovikko_counts.buf$count)*100, 2), '%'))
text(20, ymax.buf-65, paste('Total points: ', length(ruovikko1.buf$ruovikko_binary_201907_ver2)))



