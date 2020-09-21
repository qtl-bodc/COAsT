"""
AMM15_example_plot.py 

Make simple AMM15 SST plot.

"""

#%%
import coast
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as colors # colormap fiddling

#################################################
#%%  Loading  data
#################################################


config = 'AMM7'
dir_nam = "/work/sarzed/campus/analysis/northsea/"
fil_nam = "northsea.mersea.grid_U_timeseries.nc"
dom_nam = "/login/jelt/Desktop/domain_CO6.nc"
#dom_nam = "/work/sarzed/campus/grid/CO6_mesh/mesh_?gr_AMM7_CO6.nc"  
#dom_nam = "/work/sarzed/campus/grid/CO6_mesh/mesh_zgr_AMM7_CO6.nc"
# Actually need to try loading multiple domain files.
        

sci_u = coast.NEMO(dir_nam + fil_nam,
        dom_nam, grid_ref='u-grid', multiple=False)

sci_v = coast.NEMO(dir_nam + fil_nam.replace('U_timeseries','V_timeseries'), 
        dom_nam, grid_ref='v-grid', multiple=False)

# list variables in an object: sci_v.dataset

## Plot
sci_u.dataset.vozocrtx.isel(z_dim=0).isel(y_dim=30).plot() 
plt.show()

