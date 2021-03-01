'''
Python definitions used to aid with statistical calculations.

*Methods Overview*
    -> normal_distribution(): Create values for a normal distribution
    -> cumulative_distribution(): Integration udner a PDF
    -> empirical_distribution(): Estimates CDF empirically
'''

import numpy as np
import xarray as xr
from .logging_util import get_slug, debug, info, warn, error
import scipy

def quadratic_spline_roots(spl):
    """
    A custom function for the roots of a quadratic spline. Cleverness found at
    https://stackoverflow.com/questions/50371298/find-maximum-minimum-of-a-1d-interpolated-function
    Used in find_maxima().
    """
    roots = []
    knots = spl.get_knots()
    for a, b in zip(knots[:-1], knots[1:]):
        u, v, w = spl(a), spl((a+b)/2), spl(b)
        t = np.roots([u+w-2*v, w-u, 2*v])
        t = t[np.isreal(t) & (np.abs(t) <= 1)]
        roots.extend(t*(b-a)/2 + (b+a)/2)
    return np.array(roots)

def find_maxima(x, y, method='comp', **kwargs):
    '''
    Finds maxima of a time series y. Returns maximum values of y (e.g heights)
    and corresponding values of x (e.g. times).
    **kwargs are dependent on method.

        Methods:
        'comp' :: Find maxima by comparison with neighbouring values.
                  Uses scipy.signal.find_peaks. **kwargs passed to this routine
                  will be passed to scipy.signal.find_peaks.
        'cubic' :: Find the maxima and minima by fitting a cubic spline and
                    finding the roots of its derivative.
        DB NOTE: Currently only the 'comp' and 'cubic' method are implemented.
                Future methods include linear interpolation.

        JP NOTE: Cubic method:
            i) has ineligent fix for NaNs,
            ii) first converts x,y into np.floats64 for calc
            iii) probably assumes x,y are xr.DataArrays
    '''
    if method == 'comp':
        peaks, props = scipy.signal.find_peaks(y, **kwargs)
        return x[peaks], y[peaks]

    if method == 'cubic':
        """
        Cleverness found at
        https://stackoverflow.com/questions/50371298/find-maximum-minimum-of-a-1d-interpolated-function

        Find the extrema on a cubic spline fitted to 1d array. E.g:
        # Some data
        x_axis = np.array([ 2.14414414,  2.15270826,  2.16127238,  2.1698365 ,  2.17840062, 2.18696474,  2.19552886,  2.20409298,  2.2126571 ,  2.22122122])
        y_axis = np.array([ 0.67958442,  0.89628424,  0.78904004,  3.93404167,  6.46422317, 6.40459954,  3.80216674,  0.69641825,  0.89675386,  0.64274198])
        # Fit cubic spline
        f = interp1d(x_axis, y_axis, kind = 'cubic')
        x_new = np.linspace(x_axis[0], x_axis[-1],100)
        fig = plt.subplots()
        plt.plot(x_new, f(x_new)) # The fitted spline
        plt.plot(cr_pts, cr_vals, '+') # The extrema

        """
        # Remove NaNs
        I = np.isnan(y)
        if sum(I) > 0:
            print('find_maxima(): There were NaNs in timeseries')
            x = x[np.logical_not(I)]
            y = y[np.logical_not(I)]

        # Sort over time. Monotonic increasing
        y = y.sortby(x)
        x = x.sortby(x)

        # Convert x to float64 (assuming y is/similar to np.float64)
        if type(x.values[0]) == np.datetime64:
            x_float = x.values.astype('d')
            y_float = y.values.astype('d')
            flag_dt64 = True
        else:
            x_float = x.values.astype('d')
            y_float = y.values.astype('d')
            flag_dt64 = False

        if type(y.values[0]) != np.float64:
            print('find_maxima(): type(y)=',type(y))
            print('I was expecting a np.float64')

        # Do the interpolation
        f = scipy.interpolate.InterpolatedUnivariateSpline(x_float, y, k=3)
        cr_pts = quadratic_spline_roots(f.derivative())
        cr_vals = f(cr_pts)

        if flag_dt64:
            return cr_pts.astype('datetime64'), cr_vals
        else:
            return cr_pts, cr_vals

def doodson_x0_filter(elevation, ax=0):
    '''
    The Doodson X0 filter is a simple filter designed to damp out the main
    tidal frequencies. It takes hourly values, 19 values either side of the
    central one and applies a weighted average using:
              (1010010110201102112 0 2112011020110100101)/30.
    ( http://www.ntslf.org/files/acclaimdata/gloup/doodson_X0.html )

    In "Data Analaysis and Methods in Oceanography":

    "The cosine-Lanczos filter, the transform filter, and the
    Butterworth filter are often preferred to the Godin filter,
    to earlier Doodson filter, because of their superior ability
    to remove tidal period variability from oceanic signals."

    This routine can be used for any dimension input array.

    Parameters
    ----------
        elevation (ndarray) : Array of hourly elevation values.
        axis (int) : Time axis of input array. This axis must have >= 39
        elements

    Returns
    -------
        Filtered array of same rank as elevation.
    '''
    if elevation.shape[ax] < 39:
        print('Doodson_XO: Ensure time axis has >=39 elements. Returning.')
        return
    # Define DOODSON XO weights
    kern = np.array([1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 2, 0, 1, 1, 0, 2, 1, 1, 2,
                     0,
                     2, 1, 1, 2, 0, 1, 1, 0, 2, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1])
    kern = kern/30

    # Convolve input array with weights along the specified axis.
    filtered = np.apply_along_axis(lambda m: np.convolve(m, kern, mode=1),
                                   axis=ax, arr=elevation)

    # Pad out boundary areas with NaNs for given (arbitrary) axis.
    # DB: Is this the best way to do this?? Can put_along_axis be used instead
    filtered = filtered.swapaxes(0,ax)
    filtered[:19] = np.nan
    filtered[-19:] = np.nan
    filtered = filtered.swapaxes(0,ax)
    return filtered


def normal_distribution(mu: float=0, sigma: float=1,
                        x: np.ndarray=None, n_pts: int=1000):
    """Generates a discrete normal distribution.

    Keyword arguments:
    x     -- Arbitrary array of x-values
    mu    -- Distribution mean
    sigma -- Distribution standard deviation

    return: Array of len(x) containing the normal values calculated from
            the elements of x.
    """
    if x is None:
        x = np.linspace( mu-5*sigma, mu+5*sigma, n_pts)
    debug(f"Generating normal distribution for {get_slug(x)}")
    term1 = sigma*np.sqrt( 2*np.pi )
    term1 = 1/term1
    exponent = -0.5*((x-mu)/sigma)**2
    return term1*np.exp( exponent )

def cumulative_distribution(mu: float=0, sigma: float=1,
                            x: np.ndarray=None, cdf_func: str='gaussian'):
    """Integrates under a discrete PDF to obtain an estimated CDF.

    Keyword arguments:
    x   -- Arbitrary array of x-values
    pdf -- PDF corresponding to values in x. E.g. as generated using
           normal_distribution.

    return: Array of len(x) containing the discrete cumulative values
            estimated using the integral under the provided PDF.
    """
    debug(f"Estimating CDF using {get_slug(x)}")
    if cdf_func=='gaussian': #If Gaussian, integrate under pdf
        pdf = normal_distribution(mu=mu, sigma=sigma, x=x)
        cdf = [np.trapz(pdf[:ii],x[:ii]) for ii in range(0,len(x))]
    else:
        raise NotImplementedError
    return np.array(cdf)

def empirical_distribution(x, sample):
    """Estimates a CDF empirically.

    Keyword arguments:
    x      -- Array of x-values over which to generate distribution
    sample -- Sample to use to generate distribution

    return: Array of len(x) containing corresponding EDF values
    """
    debug(f"Estimating empirical distribution with {get_slug(x)}")
    sample = np.array(sample)
    sample = sample[~np.isnan(sample)]
    sample = np.sort(sample)
    edf = np.zeros(len(x))
    n_sample = len(sample)
    for ss in sample:
        edf[x>ss] = edf[x>ss] + 1/n_sample
    return xr.DataArray(edf)
