import itertools
import numpy as np
from scipy.signal import savgol_filter, medfilt
from scipy.ndimage import gaussian_filter1d
from statsmodels.nonparametric.smoothers_lowess import lowess
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
# from sklearn.metrics import r2_score
from astropy.timeseries import LombScargle

def contexts_in_iupac(iupac_val: str):
    """Takes a string that has IUPAC characters and returns all of the possible nucleotide sequences that fit that 
    IUPAC character as a list

    Args:
        iupac_val (str): the IUPAC format of the desired nucleotide sequences

    Returns:
        possible combinations (list): a list of all possible nucleotide combinations that fit within that iupac form
    """
    iupac_trans = {"R": "AG", "Y": "CT", "S": "GC", "W": "AT", "K": "GT",
                   "M": "AC", "B": "CGT", "D": "AGT", "H": "ACT", "V": "ACG",
                   "N": "ACGT", 'A': 'A', 'T': 'T', 'C': 'C', 'G': 'G'}
    ranges = [iupac_trans[base] for base in iupac_val]
    possible_combinations = [''.join(comb) for comb in itertools.product(*ranges)]
    return possible_combinations

def reverse_complement(seq: str):
    """returns the reverse complement of nucleotide sequences in standard or IUPAC notation

    Args:
        seq (str): sequence of DNA in standard or IUPAC form that

    Returns:
        reverse_complement (str): the reverse complement of the input sequence
    """
    # make a lookup table
    complement_table = {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C",
        "R": "Y",
        "Y": "R",
        "S": "S",
        "W": "W",
        "K": "M",
        "M": "K",
        "B": "V",
        "D": "H",
        "H": "D",
        "V": "B",
        "N": "N"
    }

    seq_rev = seq[::-1]
    complement_seq = "".join(complement_table.get(base, base) for base in seq_rev)
    return complement_seq

def smooth_data(x, y, method='moving_average', window_size=5, poly_order=2, alpha=0.5, sigma=1.0, mode='reflect'):
    """
    Smooths the data using a specified method.

    Args:
        x (array-like): The x-coordinates of the data points.
        y (array-like): The y-coordinates of the data points.
        method (str): The smoothing method to use. Can be 'moving_average', 'savgol_filter', 'loess', 'median_filter', 'gaussian_filter', or 'exponential_smoothing'.
        window_size (int): The size of the moving average or Savitzky-Golay filter window.
        poly_order (int): The polynomial order for the Savitzky-Golay filter.
        alpha (float): The smoothing factor for exponential smoothing.
        sigma (float): The standard deviation for Gaussian filter.
        mode (str): The mode parameter for the median filter and Gaussian filter.

    Returns:
        tuple: A tuple containing the smoothed x and y-coordinates.
    """
    if method == 'moving_average':
        weights = np.repeat(1.0, window_size) / window_size
        smoothed_y = np.convolve(y, weights, 'valid')
        shift = (window_size - 1) // 2
        smoothed_x = x[shift:len(x) - shift]
    elif method == 'savgol_filter':
        smoothed_y = savgol_filter(y, window_size, poly_order)
        smoothed_x = x
    elif method == 'loess':
        smoothed_y = lowess(y, x, frac=1./window_size)[:, 1]
        smoothed_x = x
    elif method == 'median_filter':
        smoothed_y = medfilt(y, window_size)
        smoothed_x = x
    elif method == 'gaussian_filter':
        smoothed_y = gaussian_filter1d(y, sigma=sigma, mode=mode)
        smoothed_x = x
    elif method == 'exponential_smoothing':
        smoothed_y = exponential_smoothing(y, alpha)
        smoothed_x = x
    else:
        raise ValueError("Invalid method specified.")

    return smoothed_x, smoothed_y

def find_periodicity(x, y, avg_period):
    # Calculate power spectrum using Lomb-Scargle periodogram
    freq, power = LombScargle(x, y).autopower()
    period = 1 / freq

    # Find frequency window around average period
    period_diff = np.abs(period - avg_period)
    period_window = period[period_diff < 2]
    freq_window = freq[period_diff < 2]
    power_window = power[period_diff < 2]

    # Check if no suitable period found
    if len(period_window) == 0:
        return None

    # Calculate confidence as sum of power in frequency window
    confidence = np.sum(power_window)

    # Find dominant period in window
    period = 1 / freq_window[np.argmax(power_window)]

    # Calculate signal-to-noise ratio
    signal = np.max(y) - np.min(y)
    noise = np.std(y)
    snr = signal / noise

    return period, confidence, snr

def exponential_smoothing(y, alpha):
    """
    Applies exponential smoothing to the data.

    Args:
        y (array-like): The y-coordinates of the data points.
        alpha (float): The smoothing factor.

    Returns:
        array-like: The smoothed y-coordinates.
    """
    n = len(y)
    smoothed = np.zeros(n)
    smoothed[0] = y[0]
    for i in range(1, n):
        smoothed[i] = alpha * y[i] + (1 - alpha) * smoothed[i-1]
    return smoothed

def fit_curve(x, y):
    """
    Fits multiple models to a set of data points and selects the best model based on R-squared.

    Args:
        x (array-like): The x-coordinates of the data points.
        y (array-like): The y-coordinates of the data points.

    Returns:
        tuple: A tuple containing the parameters of the best fitted curve and a matplotlib plt object.
    """
    def linear_func(x, a, b):
        return a * x + b

    def exponential_func(x, a, b, c):
        return a * np.exp(-b * x) + c

    def power_func(x, a, b, c):
        return a * np.power(x, b) + c

    def sigmoid_func(x, a, b, c, d):
        return a / (1 + np.exp(-b * (x - c))) + d

    initial_guess = [1, 1, 1]
    functions = [linear_func, exponential_func, power_func, sigmoid_func]

    best_params = None
    best_r_squared = -np.inf
    best_plt_obj = None

    for func in functions:
        try:
            popt, pcov = curve_fit(func, x, y, p0=initial_guess)
            y_pred = func(x, *popt)
            r_squared = r2_score(y, y_pred)

            if r_squared > best_r_squared:
                best_params = popt
                best_r_squared = r_squared

                x_fit = np.linspace(min(x), max(x), 100)
                y_fit = func(x_fit, *popt)

                best_plt_obj, = plt.plot(x_fit, y_fit, label='Best fit')
        except:
            pass

    return best_params, best_plt_obj

def interpolate_missing_data(x, y, x_min, x_max, method='linear'):
    # Create an array with all integers between x_min and x_max
    x_all = np.arange(x_min, x_max+1)
    
    # Find the indices of the available data points in the x array
    idx = np.where((x >= x_min) & (x <= x_max))[0]
    
    # Use the specified method to interpolate the missing data points
    if method == 'linear':
        y_interp = np.interp(x_all, x[idx], y[idx])
    elif method == 'quadratic':
        y_interp = np.interp(x_all, x[idx], y[idx], left=y[idx[0]], right=y[idx[-1]], period=None)
        y_interp = np.interp(x_all, x_all[~np.isnan(y_interp)], y_interp[~np.isnan(y_interp)], left=np.nan, right=np.nan, period=None)
        y_interp = np.interp(x_all, x_all[~np.isnan(y_interp)], y_interp[~np.isnan(y_interp)], left=np.nan, right=np.nan, period=None)
    elif method == 'cubic':
        y_interp = np.interp(x_all, x[idx], y[idx], left=y[idx[0]], right=y[idx[-1]], period=None)
        y_interp = np.interp(x_all, x_all[~np.isnan(y_interp)], y_interp[~np.isnan(y_interp)], left=np.nan, right=np.nan, period=None)
        y_interp = np.interp(x_all, x_all[~np.isnan(y_interp)], y_interp[~np.isnan(y_interp)], left=np.nan, right=np.nan, period=None)
        y_interp = np.interp(x_all, x_all[~np.isnan(y_interp)], y_interp[~np.isnan(y_interp)], left=np.nan, right=np.nan, period=None)
    elif method == 'nearest':
        y_interp = np.interp(x_all, x[idx], y[idx], left=y[idx[0]], right=y[idx[-1]], period=None)
        y_interp = np.round(y_interp).astype(int)
    
    # Return the new x and y arrays
    return x_all, y_interp
