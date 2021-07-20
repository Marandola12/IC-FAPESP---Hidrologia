
import sys
from numpy.lib.function_base import place
import pandas as pd
import numpy as np
from numpy import log as ln
import matplotlib.pyplot as plt
from netCDF4 import Dataset

# Este trecho de código controla os warnings do python
# "ignore" silencia todos os warnings
#  mude de "ignore" por "error" para tranformar warnings em erros

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

# Valores usados do mapa apenas em um grid (1830, 2380) (/10 por conta do resample)
# Código final precisa remover a coordenada especifica


# Topsoil
dt_ws = Dataset(
    'Topsoil/R aggregation/resampled rasters/NetCDF/WS.nc').variables['WS'][:]
map_ws = np.flipud(dt_ws.__array__())[183, 238]
dt_fc = Dataset(
    'Topsoil/R aggregation/resampled rasters/NetCDF/FC.nc').variables['FC'][:]
map_fc = np.flipud(dt_fc.__array__())[183, 238]
dt_wp = Dataset(
    'Topsoil/R aggregation/resampled rasters/NetCDF/WP.nc').variables['WP'][:]
map_wp = np.flipud(dt_wp.__array__())[183, 238]

# Subsoil
dt_subws = Dataset(
    'Subsoil/R aggregation/resampled rasters/NetCDF/S_WS.nc').variables['WS'][:]
map_subws = np.flipud(dt_subws.__array__())[183, 238]
dt_subfc = Dataset(
    'Subsoil/R aggregation/resampled rasters/NetCDF/S_FC.nc').variables['FC'][:]
map_subfc = np.flipud(dt_subfc.__array__())[183, 238]
dt_subwp = Dataset(
    'Subsoil/R aggregation/resampled rasters/NetCDF/S_WP.nc').variables['WP'][:]
map_subwp = np.flipud(dt_subwp.__array__())[183, 238]

# layer objects (ly1 = 0.3 m; ly2 = 0.7 m; total = 1m)
layer1 = 0  # initial water content for the test
wmax1 = map_ws

layer2 = 0
wmax2 = map_subws

# drainage rate functions (output in mm/h)


def B_func(Th33, Th1500):   # coefficient of moisture-tension
    B = (ln(1500) - ln(33)) / (ln(Th33) - ln(Th1500))

    def lbd_func(B):        # slope of logarithmic tension-moisture curve
        lbd = 1 / B
        return lbd
    return lbd_func(B)

# saturated soil conductivity


def ksat_func(ThS, Th33, lbd):
    ksat = 1930 * (ThS - Th33) ** (3 - lbd)
    return ksat

# unsaturated soil conductivity


def kth_func(Th, ThS, lbd, ksat):
    if lbd == 0:
        return 0
    if ThS == 0:
        return 0
    if Th < 0:
        Th = 0.0
    kth = ksat * (Th / ThS) ** (3 + (2 / lbd))

    # print(ksat, Th, ThS, lbd)
    return kth

# layer water flow

# precisa de uma forma de retirar evapotranspiração das duas camadas de maneira proporcional a partir de um input só
# teria como plotar o runoff no mesmo grafico sem estragar as unidades?

def update_pool(prain, evapo):
    global layer1, layer2

    # evapo division to both layers, 70% to l1, 30% to l2:

    evapo1 = evapo * 0.70
    evapo2 = evapo * 0.30 * 300 / 700
    # esses numeros são pela proporção 70/30 e também porque os valores gerados de evapo seriam v/v pra a layer 1
    # entao pra l2 eu voltei pra mm (*300) e passei pra v/v pra l2 (/700)

    # water content calculation:

    layer1 = layer1 + prain
    layer1 = layer1 - evapo1
    layer2 = layer2 - evapo2

    # water uptake já entra na transpiração, a nao ser quando há crescimento da planta
    # cálculo antigo do water content:
    # layer1 = layer1 + prain
    # layer1 = layer1 - evapo

    runoff = 0.0
    # adaptei o plot pra dar o runoff em mm (n faz sentido o runoff em v/v pq vem de duas camadas e vai sair pra outro grid)
    runoff1 = 0.0
    runoff2 = 0.0


    if layer1 > wmax1:  # saturated soil
        runoff1 += layer1 - wmax1
        runoff1 = runoff1 * 300      # conversion to mm
        runoff += runoff1
        layer1 = wmax1
        lbd = B_func(map_fc, map_wp)
        flux1_mm = ksat_func(wmax1, map_fc, lbd) * 24  # output in mm/day
        flux1_tol1 = flux1_mm / 300
        flux1_tol2 = flux1_mm / 700            # v/v conversion for layer 2
    else:
        lbd = B_func(map_fc, map_wp)
        ksat = ksat_func(map_ws, map_fc, lbd)
        flux1_mm = kth_func(layer1, map_ws, lbd, ksat) * 24
        flux1_tol1 = flux1_mm / 300
        flux1_tol2 = flux1_mm / 700

    if layer2 > wmax2:
        runoff2 += layer2 - wmax2
        runoff2 = runoff2 * 700       # conversion to mm
        runoff += runoff2
        layer2 = wmax2
        lbd = B_func(map_subfc, map_subwp)
        ksat = ksat_func(map_subws, map_subfc, lbd)
        flux2_mm = kth_func(wmax2, map_subws, lbd, ksat) * 24
        flux2 = flux2_mm / 700

    else:
        lbd = B_func(map_subfc, map_subwp)
        ksat = ksat_func(map_subws, map_subfc, lbd)
        flux2_mm = kth_func(layer2, map_subws, lbd, ksat) * 24
        flux2 = flux2_mm / 700

    layer1 -= flux1_tol1
    layer2 += flux1_tol2
    layer2 -= flux2

    # print(f'f1 to l1 is {flux1_tol1}, f1 to l2 is {flux1_tol2} and f2 is {flux2}')

    return runoff


# initial 0 values
l1values = [layer1, ]
l2values = [layer2, ]
roffvalues = [0.0, ]



# prainvalues = [0,]

# test run
# iteration test for 10000 values
for x in range(10000):
    prain = np.random.uniform(0.005, 0.1)
    evapo = np.random.uniform(0.0089, 0.0190)

    roff = update_pool(prain, evapo)
    # prainvalues.append(prain)
    l1values.append(layer1)
    l2values.append(layer2)
    roffvalues.append(roff)

# Converte as listas em arrays

l1values = np.array(l1values)
l2values = np.array(l2values)
roffvalues = np.array(roffvalues)

# se converter pra mm da pra ver que a proporção fica igual antes

# l1values = l1values * 300
# l2values = l2values * 700

# Cria um dicionário com os arrays
# Cada chave será o nome de uma coluna que vai ter os valores desejados
um_dict = {'L1': l1values,
           'L2': l2values,
           'R': roffvalues}

df = pd.DataFrame(um_dict)
print("Um dataframe com os dados:\n\n", df.head(20))
################################################################################

# # show results
plt.style.use('ggplot')
# layer1 graph
df.L1.rolling(365).mean().plot(color='#196F3D', linewidth=0.9)
plt.grid(True)
# layer2 graph
df.L2.rolling(365).mean().plot(color='#195F5D', linewidth=0.9)
# layer3 graph
df.R.rolling(365).mean().plot(color='#FF0FF0', linewidth=0.9)
plt.title('Water and runoff in the soil layers for 10000 days')
plt.xlabel('Days')
plt.ylabel('Water content (v/v)')
plt.legend(['Layer 1', 'Layer 2', 'Runoff'], loc='best',
           bbox_to_anchor=(0.5, 0., 0.5, 0.5))
# Use plt.savefig para salvar em alta resolução
# plt.savefig('grafico1.png', dpi=600)
plt.show()
