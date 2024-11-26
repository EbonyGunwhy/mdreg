"""
===============================================
Example: Poor Model Fitting
===============================================

This example illustrates the effect of poor model fitting on coregistration
for the 3D Variable Flip Angle (VFA) dataset used in the 3D data example.

As in the related 3D VFA example the data are fetched using the `fetch` 
function, the VFA parameters are defined, and the coregistration parameters are
set. The model-driven coregistration is performed, and the results are 
visualized.

Differently from the previous example, the model fit shows poor fitting and the
resulting coregistration creates significant defects in the coregistered data.

"""

#%% 
# Import packages and data
# ----------------------------
# Example data can be easily loaded in using the `fetch` function.

import numpy as np
import mdreg
import time
import matplotlib.pyplot as plt
import math

data = mdreg.fetch('VFA')

#%% 
# Extract the desired slice from the data array
# ----------------------------
# As an intial step, we will extract the 4D data (x,y,z,t) from the fetched data dictionary.

array = data['array']

#%%
# Signal model theory
# ----------------------------
# The signal model used in this example is the non-linear variable flip angle 
# SPGR model. The signal model is defined by the following equation:
#
# :math:`S(\phi)=S_{0} \frac{\sin{\phi}e^{-\frac{T_{R}}{T_{1}}}}{1-\cos{\phi}e^{-\frac{T_{R}}{T_{1}}}}`
#
# Where :math:`S` is the signal, :math:`S_{0}` the initial signal, :math:`\phi`
# the flip angle, :math:`T_{R}` the reptition time and :math:`T_{1}` the 
# longitudinal relaxtion time.  Using this equation, :math:`T_{1}` and 
# :math:`S_{0}` are optimised via a least squares method.
#

#%%
# Define model fit parameters
# ----------------------------
# The image fitting settings dictionary (`vfa_fit` in this case) is required by 
# `mdreg.fit` to fit a specific signal model to the data. Leaving this as None 
# will fit a constant model to the data as a default.
#
# Here, we select the model function `func` to be the non-linear varaible flip 
# angle SPGR model from the model library (`mdreg.spgr_vfa_nonlin`). This model 
# fit requires the flip angle values in radians (`FA`) and the repetition time 
# in seconds (`TR`). This information is provided in the `data` dictionary for 
# this example.

vfa_fit = {
    'func':  mdreg.spgr_vfa_nonlin,  # The function to fit the data
    'FA': data['FA'],  # The flip angles in degrees
    'TR': 3.71/1000  # The TR value in s
}

#%%
# Define the coregistration parameters
# ----------------------------
# The coregistration parameters are set in the `coreg_params` dictionary.
# The `package` key specifies the coregistration package to be used, with a 
# choice of elastix, skimage, or dipy.
#
# The `params` key specifies the parameters required by the chosen 
# coregistration package. Here None is used to specify default parameters for 
# freeform registration included by `mdreg`.
#
# Here, we use the elastix package with the following parameters:


coreg_params = {
    'package': 'elastix',
    'params': mdreg.elastix.params(FinalGridSpacingInPhysicalUnits='150.0'),
    'spacing': data['spacing']
}

#%%
# Define the plotting parameters
# ----------------------------
# The plotting parameters are set in the `plot_settings` dictionary.
#
# The `interval` key specifies the time interval between frames in 
# milliseconds, and the `vmin`/`vmax` keys specify the minimum/maximum value of 
# the colorbar. 
# 
# The `slice` key specifies the slice to be displayed in the 
# animation. If unset or set to None, the central slice is displayed by 
# default. 
# 
# If you are interested to save the resulting animation, you can use 
# the `path` key to the desired file path and the `filename` key to the desired 
# filename. As a default these are set to None resulting in the animation being 
# displayed on screen only. For more plotting keyword arguements, see the 
# `mdreg.plot` module.
# 

plot_settings = {
    'interval' : 500, # Time interval between animation frames in ms
    'vmin' : 0, # Minimum value of the colorbar
    'vmax' : np.percentile(array,99), # Maximum value of the colorbar
    'path' : None, # Path to save the animation
    'show' : True, # Display the animation on screen
    'filename' : None, # Filename to save the animation
    'slice' : None # No slice specified, show all slices for 3D data
}

#%% 
# Perform model-driven coregistration
# ----------------------------
# The `mdreg.fit` function is used to perform the model-driven coregistration.
# The function requires the 4D data array, the fit_image dictionary, and the 
# coregistration parameters we have already defined.
# The `verbose` parameter can be set to 0, 1, 2, or 3 to control the level of 
# output.

stime = time.time()

coreg, defo, fit, pars = mdreg.fit(array,
                                   fit_image = vfa_fit, 
                                   fit_coreg = coreg_params,
                                   maxit=3, 
                                   verbose=0)

tot_time = time.time() - stime

print(f"Non-linear fitting time elapsed: {(int(tot_time/60))} mins, {np.round(tot_time-(int(tot_time/60)*60),1)} s")

#%% 
# Visualise coregistration results
# ---------------------------------
# To easily visualise the output of the employ the `mdreg.plot` module to 
# easily produce animations that render on screen or save as a gif.
# Here we utilise `mdreg.plot_series` which accepts both 2D and 3D spatial data 
# arrays which change over an additional dimension (e.g. time or FA in this 
# case). This displays the orginal data, the fitted data and the coregistered 
# data. 
# 
# For the case of 3D data, by default the function renders animations for all 
# slices for the original, fitted and coregistered data in seperate figures. If
# a `slice` parameter is specified in the plotting parameters, the function
# will produce a single figure for the specified slice showing the original,
# fitted and coregistered data animations side-by-side.
#

anim = mdreg.animation(array, title='Original Data', **plot_settings)

#%%
anim = mdreg.animation(coreg, title='Coregistered', **plot_settings)

#%%
anim = mdreg.animation(fit, title='Model Fit', **plot_settings)

#%% 
# Export all series at once
# ----------------------------
# The `mdreg.plot_series` function can be used to plot the original, fitted and
# coregistered data for all slices in the data array. This function can also
# be used to save the animations to a file. 
#
# We include the `mdreg.animation` function to display the animations on screen
# within the documentation, but recommend using the `mdreg.plot_series` function
# to easily process and save the animations to a file when running locally.
#  >>> anims = mdreg.plot_series(array, fit, coreg, **plot_settings)

#%% 
# Identifiying poor model fitting
# ------------------------------
# 
# The coregistration results show significant defects in the coregistered data.
# This is due to poor model fitting, which usually results from optimisation to
# a local minimum rather than the global minimum.
# 
# This poor model fitting is evident from
# the model fitting from the initial iteration. For subsequent iterations the 
# model fitting become increasing unstable due to the effect of compenstating
# deformation fields.
#
# To identify poor model fitting, the user can inspect the model fitting by 
# outputing the model fitting outcomes an probing a goodness of fit metric 
# against the original uncoregistred data.
# 
# Here we calculate the chi squared value for each pixel in the data array
# after two iteration of the model fitting, and visualise the results.

coreg_1iter, defo_1iter, fit_1iter, pars_1iter = mdreg.fit(array,
                                                            fit_image = vfa_fit, 
                                                            fit_coreg = coreg_params,
                                                            maxit=1, 
                                                            verbose=0)

# Determine chi squared of fit pixel wise, regions where data == 0 are ignored
# and the output is zero
chi_squared = np.sum(np.divide((fit_1iter - array) ** 2, array, where=array != 0), axis=-1)

# Determine the grid size for the panels
num_slices = array.shape[2]
grid_size = math.ceil(math.sqrt(num_slices))

# Set the colormap and color limits
cmap = plt.get_cmap('viridis')
vmin = np.percentile(chi_squared, 1)
vmax = np.percentile(chi_squared, 99)

# Setup the figure
fig, axes1 = plt.subplots(grid_size, grid_size, figsize=(grid_size*2, grid_size*2))
fig.subplots_adjust(wspace=0.5, hspace=0.01)

# Add a title to the figure
titlesize = 10
fig.suptitle('Goodness of Fit\n \n', fontsize=titlesize+2)

# Improve the layout
plt.tight_layout()

# Plot the chi squared values for each slice
for i in range(grid_size * grid_size):
    row = i // grid_size
    col = i % grid_size
    if i < num_slices:
        im = axes1[row, col].imshow(chi_squared[:, :, i].T, cmap=cmap, vmin=vmin, vmax=vmax)
        axes1[row, col].set_title('Slice {}'.format(i+1), fontsize=titlesize)
    else:
        axes1[row, col].axis('off')  # Turn off unused subplots
    axes1[row, col].set_xticks([])  # Remove x-axis ticks
    axes1[row, col].set_yticks([])  # Remove y-axis ticks

# Set the colorbar to have overflow and underflow colors
im.cmap.set_over('red')
im.cmap.set_under('white')

# set colorbar axis: [left, bottom, width, height]
cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
cbar = fig.colorbar(im, cax=cbar_ax, extend='both')

# Add a label to the colorbar and adjust the layout to make space for the 
# colorbar
cbar.set_label('Chi Squared', rotation=270, labelpad=15)  
fig.subplots_adjust(right=0.89)

plt.show()

#%%
# Goodness of fit
# ----------------------------
# The chi squared values in the figure above show large regions of poor fit
# across the data array. These regions are highlighted in red as above the 99th
# percentile of the chi squared values. These region also correspond to the 
# regions of strange coregtistration behaviour shown in the previous animations.
# 
# The user can use this information to identify regions of poor fit and decide 
# whether to adjust the model fitting parameters or the coregistration options.

# sphinx_gallery_start_ignore

# Choose the last image as a thumbnail for the gallery
# sphinx_gallery_thumbnail_number = -1

# sphinx_gallery_end_ignore