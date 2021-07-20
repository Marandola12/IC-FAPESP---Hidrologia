library(raster)

setwd("M:/bckup/LabTerra/caete_hidro_2-master")

FC <- raster("FC.nc4")
WS <- raster("WS.nc4")
WP <- raster("WP.nc4")


aggregate(FC, 10, mean)
aggregate(WS, 10, mean)
aggregate(WP, 10, mean)

summary(FC)
summary(WS)
summary(WP)