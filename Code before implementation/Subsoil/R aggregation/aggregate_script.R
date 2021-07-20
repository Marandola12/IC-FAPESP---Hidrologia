library(raster)
library(ncdf4)
library(rgdal)

setwd("M:/LabTerra/caete_hidro_subsoil/output_maps")

FC <- raster("S_FC.nc4")
WS <- raster("S_WS.nc4")
WP <- raster("S_WP.nc4")


res_FC <- aggregate(FC, 10, mean)
res_WS <- aggregate(WS, 10, mean)
res_WP <- aggregate(WP, 10, mean)

writeRaster(res_FC,"M:/LabTerra/caete_hidro_subsoil/R aggregation/resampled rasters/S_FC.tif",format="GTiff")
writeRaster(res_WS,"M:/LabTerra/caete_hidro_subsoil/R aggregation/resampled rasters/S_WS.tif",format="GTiff")
writeRaster(res_WP,"M:/LabTerra/caete_hidro_subsoil/R aggregation/resampled rasters/S_WP.tif",format="GTiff")

plot(res_FC)

