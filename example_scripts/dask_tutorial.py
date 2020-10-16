"""
dask_tutorial

Following the notes in the documentation
https://british-oceanographic-data-centre.github.io/COAsT/docs/contributing_package/dask/

Speed to subset and process data. Subset is large than 1/2 the domain in y but less than half in x
{'x': 10, 'y': 10, 'time_counter': 10}. Speed: 2 seconds
{'x': 8, 'y': 8, 'time_counter': 10}. Speed: 3 seconds
{'x': 5, 'y': 5, 'time_counter': 5}. Speed: 20 seconds
{'x': 4, 'y': 4, 'time_counter': 10}. Speed: 92 seconds
{'x': 4, 'y': 4, 'time_counter': 3}. Speed: 36 seconds
{'x': 4, 'y': 4, 'time_counter': 3}. Speed: 22 seconds
{'x': 3, 'y': 3, 'time_counter': 3}. Speed: 58 seconds
{'x': 2, 'y': 1, 'time_counter': 3}. Speed: 337 seconds
"""

#%%
import coast
import numpy as np
#import xarray as xr
import dask
#import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
#import matplotlib.colors as colors # colormap fiddling
import logging

## Initialise logging and save to log file
log_file = open("unit_testing/unit_test.log", "w") # Need log_file.close()
coast.logging_util.setup_logging(stream=log_file, level=logging.ERROR)

#################################################
#%%  Loading and initialising methods ##
#################################################
dom_nam = "/projectsa/anchor/NEMO/AMM60/mesh_mask.nc"
dir_nam = '/projectsa/NEMO/jelt/AMM60_ARCHER_DUMP/AMM60smago/EXP_NSea/OUTPUT/'
fil_nam = 'AMM60_1h_20120204_20120208_NorthSea.nc'

chunks = {"x":10, "y":10, "time_counter":10}
sci_w = coast.NEMO(dir_nam + fil_nam, dom_nam, grid_ref='w-grid',
                   chunks=chunks )
sci_w.dataset = sci_w.dataset.swap_dims({'depthw':'z_dim'})
#################################################
#%% subset of data and domain ##
#################################################
# Pick out a North Sea subdomain
now = np.datetime64('now')
ind_sci = sci_w.subset_indices([51,-4], [60,15])
sci_nwes_w = sci_w.isel(y_dim=ind_sci[0], x_dim=ind_sci[1]) #nwes = northwest europe shelf

# Compute a diffusion from w-vel
Kz = (sci_nwes_w.dataset.wo * sci_nwes_w.dataset.e3_0).sum(dim='z_dim').mean(dim='t_dim')
print(f"{chunks}. Speed: {str(np.datetime64('now','s')-now)}")



# plot map
lon =  sci_nwes_w.dataset.longitude.squeeze()
lat =  sci_nwes_w.dataset.latitude.squeeze()

fig = plt.figure()
plt.rcParams['figure.figsize'] = 8,8

fig = plt.figure()
plt.rcParams['figure.figsize'] = 8,8
plt.pcolormesh(lon, lat, Kz.squeeze(), shading='auto', cmap='seismic')
plt.title("Kz(w)")
plt.clim([-50e-3,50e-3])
plt.colorbar()
#fig.savefig("")


#%% Close log file
#################################################
log_file.close()
