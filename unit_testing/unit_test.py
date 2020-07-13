"""
Script to do unit testing

Written as procedural code that plods through the code snippets and tests the
outputs or expected metadata.

Run:
ipython: cd COAsT; run unit_testing/unit_test.py  # I.e. from the git repo.
"""

import coast
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

dn_files = "./example_files/"
dn_fig = 'unit_testing/figures/'
fn_nemo_grid_t_dat = 'nemo_data_T_grid.nc'
fn_nemo_grid_u_dat = 'nemo_data_U_grid.nc'
fn_nemo_grid_v_dat = 'nemo_data_V_grid.nc'
fn_nemo_dat = 'COAsT_example_NEMO_data.nc'
fn_nemo_dom = 'COAsT_example_NEMO_domain.nc'
fn_altimetry = 'COAsT_example_altimetry_data.nc'

sec = 1
subsec = 96 # Code for '`' (1 below 'a')

#################################################
## ( 1 ) Test Loading and initialising methods ##
#################################################

#-----------------------------------------------------------------------------#
# ( 1a ) Load example NEMO data (Temperature, Salinity, SSH)                  #
#                                                                             #
subsec = subsec+1

try:
    sci = coast.NEMO(dn_files + fn_nemo_dat) 
    
    # Test the data has loaded
    sci_attrs_ref = dict([('name', 'AMM7_1d_20070101_20070131_25hourm_grid_T'),
                 ('description', 'ocean T grid variables, 25h meaned'),
                 ('title', 'ocean T grid variables, 25h meaned'),
                 ('Conventions', 'CF-1.6'),
                 ('timeStamp', '2019-Dec-26 04:35:28 GMT'),
                 ('uuid', '96cae459-d3a1-4f4f-b82b-9259179f95f7')])
    
    # checking is LHS is a subset of RHS
    if sci_attrs_ref.items() <= sci.dataset.attrs.items(): 
        print(str(sec) + chr(subsec) + " OK - NEMO data loaded: " + fn_nemo_dat)
    else:
        print(str(sec) + chr(subsec) + " X - There is an issue with loading " + fn_nemo_dat)
except:
    print(str(sec) + chr(subsec) +" FAILED")

#-----------------------------------------------------------------------------#
# ( 1b ) Load example NEMO domain                                             #
#                                                                             #
subsec = subsec+1

try:
    sci_dom = coast.DOMAIN(dn_files + fn_nemo_dom)
    
    # Test the data has loaded
    sci_dom_attrs_ref = dict([('DOMAIN_number_total', 1),
                  ('DOMAIN_number', 0),
                  ('DOMAIN_dimensions_ids', np.array([1, 2], dtype=np.int32)),
                  ('DOMAIN_size_global', np.array([297, 375], dtype=np.int32)),
                  ('DOMAIN_size_local', np.array([297, 375], dtype=np.int32)),
                  ('DOMAIN_position_first', np.array([1, 1], dtype=np.int32)),
                  ('DOMAIN_position_last', np.array([297, 375], dtype=np.int32)),
                  ('DOMAIN_halo_size_start', np.array([0, 0], dtype=np.int32)),
                  ('DOMAIN_halo_size_end', np.array([0, 0], dtype=np.int32)) ] )
    
    err_flag = False
    for key,val in sci_dom_attrs_ref.items():
        # There is somewhere a difference between the arrays
        if (sci_dom.dataset.attrs[key] - val ).any(): 
            print(str(sec) + chr(subsec) + " X - There is an issue with loading " + fn_nemo_dom)
            print( sci_dom.dataset.attrs[key], ': ',val, ': ', 
                  (sci_dom.dataset.attrs[key] - val ).any())
            err_flag = True
    if err_flag == False:
            print(str(sec) + chr(subsec) + " OK - NEMO domain data loaded: " + fn_nemo_dom)
except:
    print(str(sec) + chr(subsec) +" FAILED")

#-----------------------------------------------------------------------------#
# ( 1c ) Load example altimetry data                                          #
#                                                                             #
subsec = subsec+1

try:
    altimetry = coast.ALTIMETRY(dn_files + fn_altimetry)
    
    # Test the data has loaded using attribute comparison, as for NEMO_data
    alt_attrs_ref = dict([('source', 'Jason-1 measurements'),
                 ('date_created', '2019-02-20T11:20:56Z'),
                 ('institution', 'CLS, CNES'),
                 ('Conventions', 'CF-1.6'),])
    
    # checking is LHS is a subset of RHS
    if alt_attrs_ref.items() <= altimetry.dataset.attrs.items(): 
        print(str(sec) +chr(subsec) + " OK - Altimetry data loaded: " + fn_altimetry)
    else:
        print(str(sec) + chr(subsec) + " X - There is an issue with loading: " + fn_altimetry)
except:
    print(str(sec) + chr(subsec) +" FAILED")

#-----------------------------------------------------------------------------#
# ( 1d ) Load data from existing dataset                                      #
#                                                                             #
subsec = subsec+1
try:
    ds = xr.open_dataset(dn_files + fn_nemo_dat)
    sci_load_ds = coast.NEMO()
    sci_load_ds.load_dataset(ds)
    sci_load_file = coast.NEMO() 
    sci_load_file.load(dn_files + fn_nemo_dat)
    if sci_load_ds.dataset.identical(sci_load_file.dataset):
        print(str(sec) + chr(subsec) + " OK - COAsT.load_dataset()")
    else:
        print(str(sec) + chr(subsec) + " X - COAsT.load_dataset() ERROR - not identical to dataset loaded via COAsT.load()")
except:
    print(str(sec) + chr(subsec) +" FAILED")
#-----------------------------------------------------------------------------#
# ( 1d ) Set NEMO variable name                                          #
#
subsec = subsec+1
try:
    sci = coast.NEMO(dn_files + fn_nemo_dat)
    try:
        sci.dataset.temperature
    except NameError:
        print(str(sec) + chr(subsec) + " X - variable name (to temperature) not reset")
    else:
        print(str(sec) + chr(subsec) + " OK - variable name reset (to temperature)")
except:
    print(str(sec) + chr(subsec) +" FAILED")
#-----------------------------------------------------------------------------#
# ( 1e ) Set NEMO grid attributes - dimension names                                          #
#
subsec = subsec+1
try:
    if sci.dataset.temperature.dims == ('t_dim', 'z_dim', 'y_dim', 'x_dim'):
        print(str(sec) + chr(subsec) + " OK - dimension names reset")
    else:
        print(str(sec) + chr(subsec) + " X - dimension names not reset")
except:
    print(str(sec) + chr(subsec) +" FAILED")
#-----------------------------------------------------------------------------#
# ( 1g ) Set NEMO grid attributes - grid_ref                                         #
#

subsec = subsec+1
try:
    if sci.dataset.temperature.grid_ref == 't-grid':
        print(str(sec) + chr(subsec) + " OK - grid attribute set")
    else:
        print(str(sec) + chr(subsec) + " X - grid attribute not set")
except:
    print(str(sec) + chr(subsec) +" FAILED")
    
#-----------------------------------------------------------------------------#
# ( 1gg ) Load only domain data in NEMO                #
#                                                                             #
subsec = subsec+1

pass_test = False
nemo_f = coast.NEMO( fn_domain=dn_files+fn_nemo_dom, grid_ref='f-grid' )

if nemo_f.dataset._coord_names == {'depth_0', 'latitude', 'longitude'}:
    var_name_list = []
    for var_name in nemo_f.dataset.data_vars:
        var_name_list.append(var_name)
    if var_name_list == ['e1', 'e2', 'e3_0']:
        pass_test = True
        
if pass_test:
    print(str(sec) + chr(subsec) + " OK - NEMO loaded domain data only")
else:
    print(str(sec) + chr(subsec) + " X - NEMO didn't load domain data correctly")

#-----------------------------------------------------------------------------#
# ( 1ggg ) Calculate depth_0 for t,u,v,w,f grids                 #
#                                                                             #
subsec = subsec+1    

try:
    nemo_t = coast.NEMO( fn_data=dn_files+fn_nemo_grid_t_dat, 
             fn_domain=dn_files+fn_nemo_dom, grid_ref='t-grid' )
    if not np.isclose(np.nansum(nemo_t.dataset.depth_0.values), 1705804300.0):
        raise ValueError(" X - NEMO depth_0 failed on t-grid failed")    
    nemo_u = coast.NEMO( fn_data=dn_files+fn_nemo_grid_u_dat, 
             fn_domain=dn_files+fn_nemo_dom, grid_ref='u-grid' )
    if not np.isclose(np.nansum(nemo_u.dataset.depth_0.values), 1705317600.0):
        raise ValueError(" X - NEMO depth_0 failed on u-grid failed")
    nemo_v = coast.NEMO( fn_data=dn_files+fn_nemo_grid_v_dat, 
             fn_domain=dn_files+fn_nemo_dom, grid_ref='v-grid' )
    if not np.isclose(np.nansum(nemo_v.dataset.depth_0.values), 1705419100.0):
        raise ValueError(" X - NEMO depth_0 failed on v-grid failed")
    nemo_f = coast.NEMO( fn_domain=dn_files+fn_nemo_dom, grid_ref='f-grid' )
    if not np.isclose(np.nansum(nemo_f.dataset.depth_0.values), 1704932600.0):
        raise ValueError(" X - NEMO depth_0 failed on f-grid failed")

    print(str(sec) + chr(subsec) + " OK - NEMO depth_0 calculations correct")
except ValueError as err:
            print(str(sec) + chr(subsec) + str(err))

#################################################
## ( 2 ) Test general utility methods in COAsT ##
#################################################
sec = sec+1
subsec = 96

#-----------------------------------------------------------------------------#
# ( 2a ) Copying a COAsT object                                               #
#                                                                             #
subsec = subsec+1

try:
    altimetry_copy = altimetry.copy()
    if altimetry_copy.dataset == altimetry.dataset:
        print(str(sec) +chr(subsec) + " OK - Copied COAsT object ")
    else:
        print(str(sec) +chr(subsec) + " X - Copy Failed ")
except:
    print(str(sec) + chr(subsec) +" FAILED")
    
#-----------------------------------------------------------------------------#
# ( 2b ) COAsT __getitem__ returns variable                                   #
#                                                                             #
subsec = subsec+1

try:
    if sci.dataset['sossheig'].equals(sci['sossheig']):
        print(str(sec) +chr(subsec) + " OK - COAsT.__getitem__ works correctly ")
    else:
        print(str(sec) +chr(subsec) + " X - Problem with COAsT.__getitem__ ")
except:
    print(str(sec) + chr(subsec) +" FAILED")    

#-----------------------------------------------------------------------------#
# ( 2c ) Renaming variables inside a COAsT object                             #
#                                                                             #
subsec = subsec+1
try:
    altimetry_copy.rename({'sla_filtered':'renamed'})
    if altimetry['sla_filtered'].equals(altimetry_copy['renamed']):
        print(str(sec) +chr(subsec) + " OK - Renaming of variable in dataset ")
    else:
        print(str(sec) +chr(subsec) + " X - Variable renaming failed ")
except:
    print(str(sec) + chr(subsec) +" FAILED")

#################################################
## ( 3 ) Test Transect related methods         ##
#################################################
sec = sec+1
subsec = 96

#-----------------------------------------------------------------------------#
# ( 3a ) Determining and extracting transect indices                          #
#                                                                             #
subsec = subsec+1

# Extract transect indices
nemo_t = coast.NEMO( fn_data=dn_files+fn_nemo_grid_t_dat, 
                    fn_domain=dn_files+fn_nemo_dom, grid_ref='t-grid' )
yt, xt, length_of_line = nemo_t.transect_indices([51,-5],[49,-9])

# Test transect indices
yt_ref = [164, 163, 162, 162, 161, 160, 159, 158, 157, 156, 156, 155, 154,
       153, 152, 152, 151, 150, 149, 148, 147, 146, 146, 145, 144, 143,
       142, 142, 141, 140, 139, 138, 137, 136, 136, 135, 134]
xt_ref = [134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122,
       121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109,
       108, 107, 106, 105, 104, 103, 102, 101, 100,  99,  98]
length_ref = 37


if (xt == xt_ref) and (yt == yt_ref) and (length_of_line == length_ref):
    print(str(sec) + chr(subsec) + " OK - NEMO transect indices extracted")
else:
    print(str(sec) + chr(subsec) + " X - Issue with transect indices extraction from NEMO")

#-----------------------------------------------------------------------------#
# ( 3b ) Transport velocity and depth calculations                            #
#
subsec = subsec+1

nemo_t = coast.NEMO( fn_data=dn_files+fn_nemo_grid_t_dat, 
                    fn_domain=dn_files+fn_nemo_dom, grid_ref='t-grid' )
nemo_u = coast.NEMO( fn_data=dn_files+fn_nemo_grid_u_dat, 
                    fn_domain=dn_files+fn_nemo_dom, grid_ref='u-grid' )
nemo_v = coast.NEMO( fn_data=dn_files+fn_nemo_grid_v_dat, 
                    fn_domain=dn_files+fn_nemo_dom, grid_ref='v-grid' )
nemo_f = coast.NEMO( fn_domain=dn_files+fn_nemo_dom, grid_ref='f-grid' )

# Create transect object
tran = coast.Transect( (54,-15), (56,-12), nemo_f, nemo_t, nemo_u, nemo_v )

# Currently we don't have e3u and e3v vaiables so approximate using e3t
e3u = xr.DataArray( tran.data_T.e3t_25h.values, 
                   coords={'time': tran.data_U.time},
                   dims=['t_dim', 'z_dim', 'r_dim'])
tran.data_U = tran.data_U.assign(e3=e3u)
e3v = xr.DataArray( tran.data_T.e3t_25h.values, 
                   coords={'time': tran.data_U.time},
                   dims=['t_dim', 'z_dim', 'r_dim'])
tran.data_V = tran.data_V.assign(e3=e3v)

output = tran.transport_across_AB()
# Check the calculations are as expected
if np.isclose(tran.data_tran.depth_integrated_transport_across_AB.sum(), -49.19533238588342)  \
        and np.isclose(tran.data_tran.depth_0.sum(), 2301799.05444336) \
        and np.isclose(np.nansum(tran.data_tran.normal_velocities.values), -253.6484375): 

    print(str(sec) + chr(subsec) + " OK - TRANSECT transport velocities good")
else:
    print(str(sec) + chr(subsec) + " X - TRANSECT transport velocities not good")

#-----------------------------------------------------------------------------#
# ( 3c ) Transport and velocity plotting                                      #
#
subsec = subsec+2

try:
    plot_dict = {'fig_size':(5,3), 'title':'Normal velocities'}
    fig,ax = tran.plot_normal_velocity(time=0,cmap="seismic",plot_info=plot_dict,smoothing_window=2)
    fig.tight_layout()
    fig.savefig(dn_fig + 'transect_velocities.png')
    plot_dict = {'fig_size':(5,3), 'title':'Transport across AB'}
    fig,ax = tran.plot_depth_integrated_transport(time=0, plot_info=plot_dict, smoothing_window=2)
    fig.tight_layout()
    fig.savefig(dn_fig + 'transect_transport.png')
    print(str(sec) + chr(subsec) + " OK - TRANSECT velocity and transport plots saved")
except:
    print(str(sec) + chr(subsec) + " !!!")


#################################################
## ( 4 ) Object Manipulation (e.g. subsetting) ##
#################################################
sec = sec+1
subsec = 96

#-----------------------------------------------------------------------------#
# ( 4a ) Subsetting single variable                                           #
#                                                                             #
subsec = subsec+1

try:
    # Extact the variable
    data_t =  sci.get_subset_as_xarray("temperature", xt_ref, yt_ref)
    
    # Test shape and exteme values
    if (np.shape(data_t) == (51, 37)) and (np.nanmin(data_t) - 11.267578 < 1E-6) \
                                      and (np.nanmax(data_t) - 11.834961 < 1E-6):
        print(str(sec) + chr(subsec) + " OK - NEMO COAsT get_subset_as_xarray extracted expected array size and "
              + "extreme values")
    else:
        print(str(sec) + chr(subsec) + " X - Issue with NEMO COAsT get_subset_as_xarray method")
except:
    print(str(sec) + chr(subsec) +" FAILED")    

#-----------------------------------------------------------------------------#
# ( 4b ) Indices by distance method                                           #
#                                                                             #
subsec = subsec+1

try:
    # Find indices for points with 111 km from 0E, 51N

    ind = sci_dom.subset_indices_by_distance(0,51,111)
    
    # Test size of indices array
    if (np.shape(ind) == (2,674)) :
        print(str(sec) + chr(subsec) + " OK - NEMO domain subset_indices_by_distance extracted expected " \
              + "size of indices")
    else:

        print(str(sec) + chr(subsec) + "X - Issue with indices extraction from NEMO domain " \
              + "subset_indices_by_distance method")
except:
    print(str(sec) + chr(subsec) +" FAILED")        

#-----------------------------------------------------------------------------#
# ( 4c ) Subsetting entire COAsT object and return as copy                    #
#                                                                             #
subsec = subsec+1
try:
    ind = altimetry.subset_indices_lonlat_box([-10,10], [45,60])
    altimetry_nwes = altimetry.isel(time=ind) #nwes = northwest europe shelf
    
    if (altimetry_nwes.dataset.dims['time'] == 213) :
        print(str(sec) + chr(subsec) + " OK - ALTIMETRY object subsetted using isel ")
    else:
        print(str(sec) + chr(subsec) + "X - Failed to subset object/ return as copy")
except:
    print(str(sec) + chr(subsec) +" FAILED")
#################################################
## ( 5 ) STATS Methods                         ##
#################################################
sec = sec+1
subsec = 96

#-----------------------------------------------------------------------------#
# ( 5a ) Calculate single obs CRPS values                                     #
#                                                                             #
subsec = subsec+1

crps = coast.CRPS(sci, altimetry_nwes, 'sossheig','sla_filtered', nh_radius=30)

try:
    if len(crps.dataset.crps)==len(altimetry_nwes['sla_filtered']):
        print(str(sec) + chr(subsec) + " OK - CRPS SONF done for every observation")
    else:
        print(str(sec) + chr(subsec) + " X - Problem with CRPS SONF method")
        
        if len(crps.crps)==len(altimetry_nwes['sla_filtered']):
            print(str(sec) + chr(subsec) + " OK - CRPS SONF done for every observation")
        else:
            print(str(sec) + chr(subsec) + " X - Problem with CRPS SONF method")
except:
    print(str(sec) + chr(subsec) +" FAILED")    

#-----------------------------------------------------------------------------#
# ( 5b ) Plot geographical CRPS                                               #
#                                                                             #
subsec = subsec+1
plt.close('all')
try:
    fig, ax = crps.map_plot()
    fig.savefig(dn_fig + 'crps_map_plot.png')
    #plt.close(fig)
    print(str(sec) + chr(subsec) + " OK - CRPS Map plot saved")
except:
    print(str(sec) + chr(subsec) + " X - CRPS Map plot not saved")

#-----------------------------------------------------------------------------#
# ( 5c ) Plot CDF comparisons for CRPS                                        #
#                                                                             #
subsec = subsec+1
plt.close('all')
try:
    fig, ax = crps.cdf_plot(0)
    fig.savefig(dn_fig + 'crps_cdf_plot.png')
    #plt.close(fig)
    print(str(sec) + chr(subsec) + " OK - CRPS CDF plot saved")
except:
    print(str(sec) + chr(subsec) + " X - CRPS CDF plot not saved")

#################################################
## ( 6 ) Plotting Methods                          ##
#################################################
sec = sec+1
subsec = 96

#-----------------------------------------------------------------------------#
# ( 6a ) Altimetry quick_plot()                                               #
#                                                                             #
subsec = subsec+1
plt.close('all')

try:
    fig, ax = altimetry.quick_plot('sla_filtered')
    fig.savefig(dn_fig + 'altimetry_quick_plot.png')
    #plt.close(fig)
    print(str(sec) + chr(subsec) + " OK - Altimetry quick plot saved")
except:
    print(str(sec) + chr(subsec) + " X - Altimetry quick plot not saved")

plt.close('all')
