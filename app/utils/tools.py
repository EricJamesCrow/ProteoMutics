import itertools
import numpy as np
from scipy.signal import savgol_filter, medfilt
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d
from statsmodels.nonparametric.smoothers_lowess import lowess
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from astropy.timeseries import LombScargle
import pandas as pd
import subprocess
from pathlib import Path


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

def mutation_combinations(mut_type: str):
    """Takes a mutation type in the format N>N and returns a list of all possible nucleotide mutations.

    Args:
        mut_type (str): the mutation type in the format N>N

    Returns:
        possible_mutations (list): a list of all possible nucleotide mutations
    """
    iupac_trans = {
        "R": "AG", "Y": "CT", "S": "GC", "W": "AT", "K": "GT",
        "M": "AC", "B": "CGT", "D": "AGT", "H": "ACT", "V": "ACG",
        "N": "ACGT", 'A': 'A', 'T': 'T', 'C': 'C', 'G': 'G'
    }
    
    # Split the mutation type at the '>' character
    from_nuc, to_nuc = mut_type.split('>')
    
    # Get the possible nucleotides for each side of the '>'
    from_nucs = iupac_trans[from_nuc]
    to_nucs = iupac_trans[to_nuc]
    
    # Generate all possible combinations
    possible_mutations = [f"{f}>{t}" for f in from_nucs for t in to_nucs]
    
    return possible_mutations

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

def smooth_data(x, y, method='moving_average', window_size=10, poly_order=2, alpha=0.5, sigma=1.0, mode='reflect'):
    """
    Smooths the data using a specified method.

    Args:
        x (array-like): The x-coordinates of the data points.
        y (array-like): The y-coordinates of the data points.
        method (str): The smoothing method to use. Can be 'moving_average', 'savgol_filter', 'loess', 'median_filter', 'gaussian_filter', or 'exponential_smoothing'.
        window_size (int): The size of the window for the respective filter (for loess, it's the number of points to use).
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
        
        # Calculate the difference in lengths
        diff = len(x) - len(smoothed_y)
        
        # Adjust x values based on the difference
        smoothed_x = x[diff // 2: -diff // 2]
    elif method == 'savgol_filter':
        smoothed_y = savgol_filter(y, window_size, poly_order)
        smoothed_x = x
    elif method == 'loess':
        # Here we adjust frac to be the window_size divided by the number of data points
        n = len(x)
        frac = window_size / float(n)
        smoothed_values = lowess(y, x, frac=frac)
        smoothed_y = smoothed_values[:, 1]
        smoothed_x = x  # x doesn't change
    elif method == 'median_filter':
        smoothed_y = medfilt(y, window_size)
        smoothed_x = x
    elif method == 'gaussian_filter':
        smoothed_y = gaussian_filter1d(y, sigma=sigma, mode=mode)
        smoothed_x = x
    elif method == 'exponential_smoothing':
        # Assuming this is a simple implementation of exponential smoothing
        smoothed_y = np.empty_like(y)
        smoothed_y[0] = y[0]
        for i in range(1, len(y)):
            smoothed_y[i] = alpha * y[i] + (1 - alpha) * smoothed_y[i - 1]
        smoothed_x = x
    else:
        raise ValueError("Invalid method specified.")

    return smoothed_x, smoothed_y

def find_periodicity(x, y, min_period=10, max_period=300):
    # Calculate power spectrum using Lomb-Scargle periodogram
    freq, power = LombScargle(x, y).autopower()
    period = 1 / freq

    # Filter out periods below the minimum threshold and above the maximum threshold
    valid_indices = np.where((period >= min_period) & (period <= max_period))
    period = period[valid_indices]
    power = power[valid_indices]

    # If no valid periods remain after filtering, return None
    if len(period) == 0:
        return None, None, None

    # Calculate signal-to-noise ratio for the entire dataset
    signal = np.max(y) - np.min(y)
    noise = np.std(y)
    snr = signal / noise

    # Combine power and SNR to get a combined score for each period
    combined_score = power * snr

    # Find the period with the maximum combined score
    best_period_index = np.argmax(combined_score)
    best_period = period[best_period_index]
    best_confidence = power[best_period_index]

    return best_period, best_confidence, snr

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
    
    # Extract the available data points
    x_data = x[idx]
    y_data = y[idx]
    
    # Interpolate based on the specified method
    if method == 'linear':
        y_interp = np.interp(x_all, x_data, y_data)
    elif method in ['quadratic', 'cubic', 'nearest']:
        f = interp1d(x_data, y_data, kind=method, bounds_error=False, fill_value=np.nan)
        y_interp = f(x_all)
    else:
        raise ValueError(f"Unsupported interpolation method: {method}")

    # Remove NaN values at the edges
    valid_mask = ~np.isnan(y_interp)
    x_all = x_all[valid_mask]
    y_interp = y_interp[valid_mask]

    return x_all, y_interp


def remove_cut_bias(df: pd.DataFrame, index_range: list[int], method: str = 'cubic') -> pd.DataFrame:
    """Removes data points for indices within a given range and its negative counterpart and interpolates them.

    Args:
        df (pd.DataFrame): The input dataframe.
        index_range (list[int]): List with two integers denoting the start and end of the index range.
        method (str, optional): Interpolation method. Defaults to 'cubic'.

    Returns:
        pd.DataFrame: The dataframe after removing and interpolating the specified indices.
    """
    # Check if the provided range has exactly two values
    if len(index_range) != 2:
        raise ValueError("index_range should contain exactly two integers denoting the start and end of the range.")
    
    # Create the list of indices to be removed
    remove_indices = list(range(index_range[0], index_range[1] + 1))
    remove_indices += [-i for i in remove_indices]
    
    # Drop the rows corresponding to the specified indices
    df = df.drop(remove_indices, errors='ignore')
    
    # Interpolate the missing values
    df = df.sort_index().interpolate(method=method)
    
    return df

def bedtools_getfasta(bed_file: Path, fasta_file: Path):
    """Runs `bedtools getfasta` on the input dyad file and returns fasta file.

    Args:
        dyad_file (Path): .bed file with +/- 500 generated from General.adjust_dyad_positions().
        fasta_file (Path): .fa file that is the genome fasta file associated with the dyad positions (ex: hg19.fa).
    """
    # Create a name for the new file with a .fa ending
    output_fasta_file = bed_file.with_name(f'{bed_file.stem}_{fasta_file.stem}_fasta.fa')

    # Run the bedtools getfasta tool given the input files
    command = f'bedtools getfasta -fi {fasta_file} -bed {bed_file} -fo {output_fasta_file} -tab'
    with subprocess.Popen(args=command, stdout=subprocess.PIPE, shell=True) as p:
        return p, output_fasta_file

