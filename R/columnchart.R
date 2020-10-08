## ---------------------------
##
## Purpose of script:
##
##      Create columnchart with multiple columns side by side
##
##      Notes: Plot not good
##
## Author: Ari-Pekka Jokinen
##
## Date Created: 2020-09-23
##
## Copyright (c) Ari-Pekka Jokinen, 2020
## Email: ari-pekka.jokinen@helsinki.fi
##
## ---------------------------
##
## Notes:
##   Not ready
##
## ---------------------------

library(ggplot2)

# workdir
setwd("E:/LocalData/aripekkj/ProtectedAreas/Madagascar/")
getwd()

# read csv file
df <- read.csv("Tourist_data/visitors_some_join_all_cols.csv", sep=";")

# subset data to keep the columns where year matches
df <- subset(df, select = -c(X1992, X1993, X1994, X1995, X1996, X1997, X1998, X1999, X2000, X2001, X2002, X2003, X2004, Area, X2019))

# check colnames where to calculate row sums
colnames(df[,4:17])
colnames(df[,18:31])

# check df column classes
sapply(df, class)

# change class for the columns that are used in calculations to same type
i <- c(18:31) # range of columns to change
df[, i] <- apply(df[, i], 2, function(x) as.numeric(as.character(x))) # change columns to numeric

# check df column classes
sapply(df, class)

# calculate rowsums
df$flickr_sum <- rowSums(df[,4:17], na.rm=TRUE, dims=1)
df$mnp_sum <- rowSums(df[,18:31], na.rm=TRUE, dims=1)

# plot
ggplot(data = df, aes(x=NAME)) +
  geom_col(mapping = aes(y = flickr_sum), width = 0.2,  position = "dodge2", color="blue") +
  geom_col(mapping = aes(y = mnp_sum), position = "dodge2", color="red") +
  theme(axis.text = element_text(size= 7, angle= 75, hjust = 1, vjust = 0.2)) +
  ggtitle("Visitors in MDG Protected Areas")

# df to csv
write.csv(df, file="Tourist_data/visitor_some_join_selected_columns.csv", sep=";")








