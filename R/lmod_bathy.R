"""
linear model for satellite based bathymetry and field depth

"""

library(tidyverse)
library(dplyr)
library(raster)
library(rgdal)
library(viridis)
library(mgcv)

fp = 'D://Users//E1008409//MK//freshabit//syvyysmalli//freshabit_meta_S2_Acolite_Rrs_sampled_logbandratio.csv'
#fp = 'D://Users//E1008409//MK//freshabit//syvyysmalli//biobase_logband_ndvi_sampled.csv'
fp_r = 'D://Users//E1008409//MK//freshabit//Sentinel2//acolite//bandratio/S2B_L2W_Rrs_logB02B04_3067.tif'

#fp_r2 = 'D://Users//E1008409//MK//freshabit//syvyysmalli//planet_puruvesi_logb1b3.tif'
#fp_p = 'D://Users//E1008409//MK//freshabit//syvyysmalli//puruvesi//freshabit_sampled_planet_logb1b3.csv'

fp_out = 'D://Users//E1008409//MK//freshabit//Sentinel2//acolite//S2_Rrs_logB02B04_depth_m.tif'

# read file
d = read.csv(fp, header = TRUE, sep=',')
r <- raster::stack(fp_r)#, fp_r2)

dnames <- colnames(d)

# select columns
d <- d[, c(dnames[2], dnames[3], dnames[4], dnames[5], dnames[6])]
head(d)
# rename columns
colnames(d) <- c('fid', 'field_no', 'line', 'map_method', 'field_depth', 'logbr', 'logbg', 'ndvi')       

# select 
d <- d[d$ndvi < 0.1,]
#d <- d[d$map_meth == 21,]

# create column for unique field lines from field_no and line
d$field_no <- as.character(d$field_no)
d['field_line'] <- as.factor(paste0(d$field_no, d$line))
str(d)
head(d)
# choose band ratio to model
#d <- d[c('field_depth', 'logbr')]
# rename columns
#colnames(d) <- c('field_depth', 'logb')       

# drop na rows (ie. points outside raster)
d <- drop_na(d, logbr)
# drop duplicates
#d <- d[!duplicated(d$logb), ]

# drop points where recorded depth less than 0.1m
d <- d[d$field_depth > 0.1,]
# drop points where recorded more than 6
d <- d[d$field_depth < 6,]

# rename raster layer
names(r) <- c('logb')#, 'logbg')

# plot band ratio to depth
par(mfrow=c(1,1))
plot(d$logbr, d$field_depth,
     main='S2 log band ratio to observed depth',
     xlab='Band ratio blue/red',
     ylab='Observed depth (m)')
abline(v=1.18, col='blue')


# check outliers
Q <- quantile(d$logb, probs=c(.25,.75), na.rm=FALSE)
iqr <- IQR(d$logb)
up <- Q[2] + 1.5*iqr
low <- Q[1] - 1.5*iqr
dt <- subset(d, d$logb > low & d$logb < up)

# linear model
lmod <- lm(d$field_depth~d$logb)
summary(lmod)
par(mfrow=c(2,2))
plot(lmod)


# glm
glm_mod <- glm(d$field_depth~d$logb, family = 'gaussian') # poly(d$logbr, 2)
glmsum <- summary(glm_mod)
print(glmsum)
glmr2 <- (glmsum$null.deviance-glmsum$deviance) / glmsum$null.deviance
print(glmr2)

anova(glm_mod, test='F')

# gam
gam1 <- gam(field_depth ~ s(logbr, k=3), family='gaussian', data=d)
summary(gam1)
#plot
plot(gam1, shade=TRUE)
# gam predict
predgam <- predict(object = r, model=gam1, fun=predict.gam, type='response')
# visualise prediction
#plot(predgam, main='Predicted water depth', col=viridis(10), zlim=c(0,5))
par(mfrow=c(2,2))
gam.check(gam1)

# gamm
gamm_mod <- gamm(field_depth~ s(logbr, k=3), family='gaussian', data=d, random=(list(field_line=~1, logbr=~1)))
summary(gamm_mod[[1]])
summary(gamm_mod[[2]])

# cross-validation
pred_vector <- NULL

# leave-one out cv
for (i in 1:nrow(d)) {
  deval <- d[i,]
  dcal <- d[-i,]
  # different models
  #mod <- lm(field_depth~logb, data=dcal)
  #mod <- glm(field_depth~logb, family = 'gaussian', data=dcal)
  #mod <- gam(field_depth ~ s(logbr, k=3), family='gaussian', data=dcal)
  mod <- gamm(field_depth~ s(logbr, k=3), family='gaussian', data=d, random=(list(field_line=~1, logbr=~1)))
  pred_cv <- predict(mod[[2]], deval, type='response')
  pred_vector[i] <- as.vector(pred_cv)
}

# error stats
mae <- mean(abs(d$field_depth-pred_vector))
errors <- d$field_depth-pred_vector
sq_errors <- errors^2
rmse <- sqrt(mean(sq_errors))
correlation <- cor(d$field_depth, pred_vector)

# plot evaluation data
par(mfrow=c(1,1))
plot(pred_vector, d$field_depth, main='Leave one out cross-validation (GAMM)', 
     xlab='Predicted depth (m)', 
     ylab='Field measured depth (m)',
     xlim=c(0,max(pred_vector)),
     ylim=c(0,max(d$field_depth))
     )
text(x=0.25, y=min(d$field_depth)+3.5, paste('MAE: ', as.character(round(mae, 2))))
text(x=0.25, y=min(d$field_depth)+4, paste('RMSE: ', as.character(round(rmse, 2))))
abline(0,1, col='red')


# repeated random sample validation
obs <- nrow(d)
ncal <- 0.7*obs

# empty vector for results
res <- NULL

# cross-validation 1000 rounds
for (i in 1:1000){
  s <- sample(obs, ncal, replace = FALSE)
  data_cal <- d[s,]
  data_eval <- d[-s,]
  gam_rcv <- gam(field_depth ~ s(logb, k=3), data=data_cal, family='gaussian')
  rcv_pred <- predict(gam_rcv, data_eval, type='response')
  res[i] <- cor(rcv_pred, data_eval$field_depth)
  print(i)
}

# boxplot correlations
boxplot(res, main='Model prediction/evaluation correlation (Sentinel2 data), \n1000 rounds repeated random sampling')


# write raster
writeRaster(predgam, fp_out, format='GTiff', datatype='FLT4S', NAflag=0, overwrite=TRUE)

library(sf)
# read 
bathy_fp <- 'D://Users//E1008409//MK//freshabit//Biobase_Puruvesi//Biobase_bathy_rasterized10m_mean_pts.gpkg'
bathy <- st_read(bathy_fp)
bnames <- colnames(bathy)
#sampled_fp = 'D://Users//E1008409//MK//freshabit//syvyysmalli//validation//puru_depth_planetb1b3_model_sampled.csv'

# change colnames
bathy <- bathy[, c(bnames[8], bnames[9])]
bathy$fid <- 1:nrow(bathy)
#colnames(sampled) <- c('fid', 'depth_m', 'model_depth')

# sample raster with bathy points
sampled <- raster::extract(predgam, bathy, df=TRUE)
#sampled$fid <- bathy$fid
colnames(sampled) <- c('ID', 'model_depth')

# merge 
sampled <- merge(bathy, sampled, by.x='fid', by.y='ID')

# drop na
sampled <- sampled[!is.na(sampled$model_depth),]
# remove duplicates
sampled <- sampled[!duplicated(sampled$model_depth), ]

#sampled <- sampled[sampled$depth_m < 6,] # compare depths less than

#plot
par(mfrow=c(1,2))
plot(sampled$depth_m, sampled$model_depth,
     cex=0.5,
     main='Comparison of SDB (Sentinel2) \nto bathymetry data (< 6 m)',
     xlim=c(0,10),
     ylim=c(0,10),
     xlab='Biobase bathymetry (m)',
     ylab='SDB (m)')
abline(0,1, col='red')
c <- cor(sampled$model_depth, sampled$depth_m)
mae_v <- mean(abs(sampled$depth_m-sampled$model_depth))
#rmse_v <- sqrt(mean((sampled$depth_m-sampled$model_depth)^2))
text(x=1.5, y=min(sampled$depth_m)+8, paste('MAE: ', as.character(round(mae_v, 2))))
#text(x=7, y=min(sampled$depth_m)+3, paste('RMSE: ', as.character(round(rmse_v, 2))))

val_errors <- sampled$depth_m - sampled$model_depth
val_errors_iqr <- IQR(val_errors)
quants <- quantile(val_errors, c(.05, .95))
hist(val_errors, main='')
text(3, 1500, paste('IQR: ', as.character(round(val_errors_iqr, 2))))



#text(1,max(sampled$depth_m)-0.5, paste0('Correlation: ', round(c,2)))


mae_sub <- mean(abs(sampled_sub$depth_m-sampled_sub$model_depth))
rmse_sub <- sqrt(mean((sampled_sub$depth_m-sampled_sub$model_depth)^2))


