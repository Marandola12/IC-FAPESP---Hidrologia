import numpy as np
from netCDF4 import Dataset

# PTFs de Saxton & Rawls 2006 para estimar água no solo em três condições diferentes
# Theta = Th

# Unidades de Medida:
#   C, S, e OM em decimal volume/volume
#   Th em vol/vol (valores decimais)
#   Potencial matricial em KPa
#   Plant Av. Water (PAW) = Th33 - Th1500

S = Dataset('./T_SAND.nc4')

lon = S.variables['lon'][:]
lat = S.variables['lat'][:]

S = Dataset('./T_SAND.nc4').variables['T_SAND'][:]/100
C = Dataset('./T_CLAY.nc4').variables['T_CLAY'][:]/100
OM = Dataset('./T_OC.nc4').variables['T_OC'][:]/100

#   Water soil content @ -33 kPa (Field Capacity)

def water_content_fieldcap(S, C, OM):

    Th33t = -0.251 * S + 0.195 * C + 0.011 * OM + 0.006 * \
        (S * OM) - 0.027 * (C * OM) + 0.452 * (S * C) + 0.299

    return Th33t + (1.283 * pow(Th33t, 2) - (0.374 * Th33t) - 0.015)

def water_content_saturated(S, C, OM, FC):

    ThS_minus_33t = 0.278 * S + 0.034 * C + 0.022 * OM - 0.018 * \
        (S * OM) - 0.027 * (C * OM) - 0.584 * (S * C) + 0.078
    ThS_minus_33 = ThS_minus_33t + (0.6360 * ThS_minus_33t - 0.107)

    return FC + ThS_minus_33 - 0.097 * S + 0.043

def water_content_wpoint(S, C, OM):

    Th1500t = -0.024 * S + 0.487 * C + 0.006 * OM + 0.005 * \
        (S * OM) - 0.013 * (C * OM) + 0.068 * (S * C) + 0.031

    return Th1500t + (0.14 * Th1500t - 0.02)

def save_nc(fname, arr, varname):

    nc_filename = fname

    rootgrp = Dataset(nc_filename, mode='w', format='NETCDF4')

    la = arr.shape[0]
    lo = arr.shape[1]
    # dimensions
    rootgrp.createDimension("latitude", la)
    rootgrp.createDimension("longitude", lo)
    # variables

    latitude = rootgrp.createVariable(varname="latitude",
                                      datatype=np.float32,
                                      dimensions=("latitude",))

    longitude = rootgrp.createVariable(varname="longitude",
                                       datatype=np.float32,
                                       dimensions=("longitude",))

    var_ = rootgrp.createVariable(varname=varname,
                                  datatype=np.float32,
                                  dimensions=("latitude", "longitude",),
                                  fill_value=-1,
                                  zlib=True,
                                  least_significant_digit=4)
    # attributes
    # rootgrp
    rootgrp.description = 'CAETE_HYDROLOGY'
    rootgrp.source = "darelafilho@gmail.com"

    # lat
    latitude.units = u"degrees_north"
    latitude.long_name = u"latitude"
    latitude.standart_name = u"latitude"
    latitude.axis = u'Y'

    # lon
    longitude.units = "degrees_east"
    longitude.long_name = "longitude"
    longitude.standart_name = "longitude"
    longitude.axis = 'X'

    # var
    var_.long_name = varname
    var_.units = '%'
    var_.standard_name = varname
    var_.missing_value = -1.0
    var_.no_data = -1.0

    # WRITING DATA
    longitude[:] = lon
    latitude[:] = lat

    var_[:, :] = arr
    rootgrp.close()

if __name__ == '__main__':
    WP = water_content_wpoint(S, C, OM)
    FC = water_content_fieldcap(S, C, OM)
    WS = water_content_saturated(S, C, OM, FC)

    save_nc("WP.nc4", WP, 'WP')
    save_nc("FC.nc4", FC, 'FC')
    save_nc("WS.nc4", WS, 'WS')
