import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')                                       
from app.utils import data_frame_operations, tools
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline


wt_total = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/lesion_files/vcf/SRR_treated_cellular_69-70_proteomutics/SRR_treated_cellular_69-70.counts')
wt_intersect = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/lesion_files/vcf/SRR_treated_cellular_69-70_proteomutics/SRR_treated_cellular_69-70_hg19_MNase_nucleosome_map_all.intersect')

dyads_counts = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/ProteoMuticsTest/hg19_MNase_nucleosome_map_all_proteomutics/hg19_MNase_nucleosome_map_all.counts')
genomic_counts = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/ProteoMuticsTest/hg19.counts')

new_dyads_counts = data_frame_operations.DataFormatter.reverse_complement_positional_strand_conversion(dyads_counts)
new_genomic_counts = data_frame_operations.DataFormatter.reverse_complement_tri_counts(genomic_counts)
new_wt_intersect = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/lesion_files/vcf/SRR_treated_cellular_69-70_proteomutics/SRR_treated_cellular_69-70_hg19_MNase_nucleosome_map_all_flipped.intersect')

data_formatter = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, dyads_counts, genomic_counts, wt_intersect)
data_formatter2 = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, new_dyads_counts, new_genomic_counts, new_wt_intersect)

def make_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, interpolate_method: bool = False, smoothing_method: None = None):
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    
    x = np.array(indexes)
    y = np.array(graph_values)


    if smoothing_method:
        x, y = tools.smooth_data(x, y, method=smoothing_method, window_size=55, poly_order=3)

    if interpolate_method:
        x, y = tools.interpolate_missing_data(x, y, -1000, 1000, interpolate_method)

    # Your processing with Tools methods
    overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(x, y, min_period=50)
    print(f"Overall period: {overall_period}, confidence: {overall_confidence}, signal to noise: {overall_signal_to_noise}")

    # Identify peaks based on overall_period
    peaks = [0]
    while peaks[-1] + overall_period < x[-1]:
        peaks.append(peaks[-1] + overall_period)
    while peaks[0] - overall_period > x[0]:
        peaks.insert(0, peaks[0] - overall_period)

    def in_red_region(val):
        for peak in peaks:
            if peak - 73 <= val <= peak + 73:
                return True
        return False

    # Plotting on the passed ax
    ax.scatter(x, y, c='black', s=2)
    for i in range(1, len(x)):
        if in_red_region(x[i-1]) and in_red_region(x[i]):
            ax.plot(x[i-1:i+1], y[i-1:i+1], color='red')
        else:
            ax.plot(x[i-1:i+1], y[i-1:i+1], color='blue')
    ax.set_title(title)
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
    ax.set_ylabel('Mutation Counts Normalized to Context')

def make_73_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, smoothing_method):
    # Filter the data for the desired range (-72 to +72)
    mutation_data = mutation_data[(mutation_data.index >= -72) & (mutation_data.index <= 72)]

    # Now, the 'indexes' will only contain values from -72 to +72
    indexes = mutation_data.index.tolist()
    graph_values = [sum(mutation_data.loc[item]) for item in indexes]
    
    x = np.array(indexes)
    y = np.array(graph_values)

    # Calculate the polynomial coefficients for a 2nd order polynomial
    poly_coeffs = np.polyfit(x, y, 2)
    # Generate a polynomial function from the coefficients
    poly_func = np.poly1d(poly_coeffs)

    # Generate new y values using the polynomial function
    poly_y = poly_func(x)

    # Perform linear regression to find the trend
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    # Calculate the y values of the trend line
    trend_y = intercept + slope * x

    # Print the equations of the trend line and polynomial
    print(f"Linear trend line: y = {slope:.2f}x + {intercept:.2f}")
    print(f"Polynomial trend line: y = {poly_coeffs[0]:.2f}x^2 + {poly_coeffs[1]:.2f}x + {poly_coeffs[2]:.2f}")

    if smoothing_method:
        x_smooth, y_smooth = tools.smooth_data(x, y, method=smoothing_method, window_size=5, poly_order=3)
        # x_smooth, y_smooth = x, y
        # Use spline interpolation for a smooth curve
        spline = make_interp_spline(x_smooth, y_smooth, k=3)
        x_spline = np.linspace(x_smooth.min(), x_smooth.max(), 500)
        y_spline = spline(x_spline)
        ax.plot(x_spline, y_spline, color='green', label='Smoothed Curve')

    # Plot the original data, the linear trend, and the polynomial fit
    ax.scatter(x, y, c='black', s=2, label='Original Data')  # Scatter plot of the original data
    ax.plot(x, trend_y, color='red', label='Linear Trend')   # Linear trend line
    ax.plot(x, poly_y, color='blue', label='Polynomial Fit') # Polynomial trend line

    # Setting the title and labels
    ax.set_title(title)
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
    ax.set_ylabel('Mutation Counts Normalized to Context')
    ax.legend() # Show the legend to differentiate the lines

# Create a figure and a grid of subplots with 2 rows and 1 column.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Use the first Axes (ax1) for the first function and the second Axes (ax2) for the second function.
make_graph_matplotlib(ax1, data_formatter, 'WT Dyads', smoothing_method='savgol_filter')
make_73_graph_matplotlib(ax2, data_formatter, 'WT Dyads 73', smoothing_method='savgol_filter')
# Adjust the layout of the subplots to prevent overlap.
plt.tight_layout()

# Show the plot.
plt.show()

# # Create a figure and a grid of subplots with 2 rows and 1 column.
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# # Use the first Axes (ax1) for the first function and the second Axes (ax2) for the second function.
# make_graph_matplotlib(ax1, data_formatter, 'WT Dyads', smoothing_method=None)
# make_73_graph_matplotlib(ax2, data_formatter, 'WT Dyads 73', smoothing_method=None)
# # Adjust the layout of the subplots to prevent overlap.
# plt.tight_layout()

# # Show the plot.
# plt.show()