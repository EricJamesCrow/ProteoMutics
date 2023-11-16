import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')                                       
from app.utils import data_frame_operations, tools
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
import matplotlib.lines as mlines

# Define your color palette
colors_graph1 = ['#008B8B', '#960018']  # Dark Cyan, Carmine Red
colors_graph2 = ['#4B0082', '#FF8C00', '#228B22']  # Indigo, Dark Orange, Forest Green
# plt.style.use('seaborn-whitegrid')  # A clean style for the plot
plt.rcParams['font.family'] = 'Arial'  # Set a global font family

def make_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, smoothing_method: None = None):
    # plt.style.use('seaborn-whitegrid')  # A clean style for the plot
    plt.rcParams['font.family'] = 'Arial'  # Set a global font family
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    
    ax.set_xlim([-1000, 1000])  # Set the limits for the x-axis

    x = np.array(indexes)
    y = np.array(graph_values)

    if smoothing_method:
        # Assuming tools is an object with methods for smoothing and interpolation.
        x_smooth, y_smooth = tools.smooth_data(x, y, method=smoothing_method, window_size=301, poly_order=7)
        spline = make_interp_spline(x_smooth, y_smooth, k=3)
        x_spline = np.linspace(x_smooth.min(), x_smooth.max(), 10000)
        y_spline = spline(x_spline)
    else:
        # No smoothing or interpolation, create spline data directly from raw data.
        spline = make_interp_spline(x, y, k=3)
        x_spline = np.linspace(x.min(), x.max(), 10000)
        y_spline = spline(x_spline)

    # Your processing with Tools methods to find periodicity
    overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(x_spline, y_spline, min_period=50)
    print(f"Overall period: {overall_period}, confidence: {overall_confidence}, signal to noise: {overall_signal_to_noise}")

    # X-axis range and number of data points
    x_axis_range = 1000 - (-1000)  # 2000 units
    num_data_points = 10000  # You have this many points in your spline

    # Number of data points per x-axis unit
    data_points_per_unit = num_data_points / x_axis_range

    # Desired peak width in x-axis units
    # If you want the width of the peak to be say 1/5th of the period:
    desired_peak_width_x_units = overall_period // 7

    # Convert this width to data points
    desired_peak_width_data_points = desired_peak_width_x_units * data_points_per_unit

    # Calculate peak distance as 80% of overall period in data points
    peak_distance = round(overall_period * 0.8 * data_points_per_unit)

    # For peaks
    peaks, properties = find_peaks(y_spline, distance=peak_distance, width=desired_peak_width_data_points)
    if peaks.size > 0:
        peak_x_coordinates = x_spline[peaks]
        peak_widths = properties["widths"]  # This gives you the widths of the found peaks
    else:
        peak_x_coordinates = []
        peak_widths = []

    # Now, find the index of the peak that is closest to zero
    if peaks.size > 0:
        peak_x_coordinates = x_spline[peaks]
        # Get the index within 'peak_x_coordinates' array that is closest to zero
        closest_peak_index = np.argmin(np.abs(peak_x_coordinates))
        closest_peak_to_zero = peak_x_coordinates[closest_peak_index]

        # If the closest peak is not exactly at zero, adjust it to be at zero
        if closest_peak_to_zero != 0:
            # Replace the x-coordinate of this peak with zero
            peak_x_coordinates[closest_peak_index] = 0

        # Update peaks array after setting the closest peak to zero
        peaks[closest_peak_index] = np.argmin(np.abs(x_spline - 0))

        # Now, ensure there are no peaks within 73 units of the zero peak
        valid_peak_indices = [i for i in range(len(peak_x_coordinates)) if i == closest_peak_index or np.abs(peak_x_coordinates[i]) > 73]

        # Update the 'peaks' and 'peak_x_coordinates' to only include the valid peaks
        peaks = peaks[valid_peak_indices]
        peak_x_coordinates = peak_x_coordinates[valid_peak_indices]

    def in_red_region(val):
        for peak in peak_x_coordinates:
            if peak - 73 <= val <= peak + 73:
                return True
        return False

    # Plotting on the passed ax using spline data
    ax.scatter(x, y, marker='.', s=2, color='darkgrey', alpha=0.6) # Scatter plot of the original data
    for i in range(1, len(x_spline)):
        if in_red_region(x_spline[i-1]) and in_red_region(x_spline[i]):
            ax.plot(x_spline[i-1:i+1], y_spline[i-1:i+1], color=colors_graph1[0])
        else:
            ax.plot(x_spline[i-1:i+1], y_spline[i-1:i+1], color=colors_graph1[1])

    # Set the x-axis limits based on the min and max of the spline data
    ax.set_ylim([y_spline.min()*1.10, y_spline.max()*1.10])
    # SPECIFIC USE CASE
    # ax.set_ylim([-0.1, 0.2])

    ax.set_title(title, fontsize=20, weight='bold')
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)', fontsize=16, weight='bold')
    ax.set_ylabel('Fold Change', fontsize=16, weight='bold')
    ax.tick_params(axis='both', which='major', labelsize=12)

    # Create custom legend handles
    green_line = mlines.Line2D([], [], color=colors_graph1[0], markersize=15, label='Nucleosomal DNA')
    orange_line = mlines.Line2D([], [], color=colors_graph1[1], markersize=15, label='Linker DNA')
    # black_dot = mlines.Line2D([], [], marker='.', markersize=5, color='darkgrey', linestyle='None', label='Original Data')

    # Add custom legend handles
    legend = ax.legend(handles=[green_line, orange_line], loc='upper right', fontsize=12,
                   framealpha=0.5, facecolor='white', edgecolor='black', frameon=True, 
                   borderpad=0.2, labelspacing=0.2, handletextpad=0.2)
    # ax.legend(handles=[green_line, orange_line], loc='upper right', fontsize=12)

def make_73_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, smoothing_method):
    # plt.style.use('seaborn-whitegrid')  # A clean style for the plot
    plt.rcParams['font.family'] = 'Arial'  # Set a global font family
    # Filter the data for the desired range (-72 to +72)
    mutation_data = mutation_data[(mutation_data.index >= -72) & (mutation_data.index <= 72)]

    ax.set_xlim([-72, 72])  # Set the limits for the x-axis

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
        x_spline = np.linspace(x_smooth.min(), x_smooth.max(), 10000)
        y_spline = spline(x_spline)
        ax.plot(x_spline, y_spline, color='black', label='Smoothed Curve', lw=1)

    # Your processing with Tools methods
    overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(x, y, min_period=2, max_period=25)
    print(f"Overall period: {overall_period}, confidence: {overall_confidence}, signal to noise: {overall_signal_to_noise}")

    # Calculate the distance parameter as half the period in data points
    peak_distance = round(overall_period*0.8)

    # X-axis range and number of data points
    x_axis_range = 72 - (-72)  # 144 units
    num_data_points = 10000  # You have this many points in your spline

    # Number of data points per x-axis unit
    data_points_per_unit = num_data_points / x_axis_range

    # Desired peak width in x-axis units, say you want a peak width of 2 units as an example
    desired_peak_width_x_units = overall_period // 3

    # Convert this width to data points
    desired_peak_width_data_points = desired_peak_width_x_units * data_points_per_unit

    # For peaks
    peaks, properties = find_peaks(y_spline, distance=peak_distance, width=desired_peak_width_data_points)
    if peaks.size > 0:
        peak_x_coordinates = x_spline[peaks]
        peak_widths = properties["widths"]  # This gives you the widths of the found peaks
    else:
        peak_x_coordinates = []
        peak_widths = []

    # Similarly for valleys, but inverted
    valleys, properties = find_peaks(-y_spline, distance=peak_distance, width=desired_peak_width_data_points)
    if valleys.size > 0:
        valley_x_coordinates = x_spline[valleys]
        valley_widths = properties["widths"]
    else:
        valley_x_coordinates = []
        valley_widths = []

    # Helper function to color a segment
    def color_segment(start, end, color):
        mask = (x_spline >= start) & (x_spline <= end)
        ax.plot(x_spline[mask], y_spline[mask], color=color, lw=2)

    # Combine the arrays
    combined_points = np.concatenate((peak_x_coordinates, valley_x_coordinates))

    # Sort the combined array
    sorted_points = np.sort(combined_points)

    # Calculate midpoints between every two points
    midpoints = (sorted_points[:-1] + sorted_points[1:]) / 2
    midpoints = np.append(midpoints, [-72, 72])
    midpoints = np.sort(midpoints)

    for i in range(len(midpoints)):
        if midpoints[i] <= 0 <= midpoints[i+1]:
            color_segment(midpoints[i], midpoints[i+1], colors_graph2[0])
            zero_index = i
    green = True
    for i in range(zero_index, -1, -1):
        if green:
            color_segment(midpoints[i-1], midpoints[i], colors_graph2[1])
            green = False
        else:
            color_segment(midpoints[i-1], midpoints[i], colors_graph2[0])
            green = True
    for i in range(zero_index + 1, len(midpoints)-1, 1):
        if green:
            color_segment(midpoints[i], midpoints[i+1], colors_graph2[1])
            green = False
        else:
            color_segment(midpoints[i], midpoints[i+1], colors_graph2[0])
            green = True

    # Plot the original data, the linear trend, and the polynomial fit
    ax.scatter(x, y, marker='.', s=10, color='darkgrey', alpha=0.6, label='Original Data')  # Scatter plot of the original data
    # ax.plot(x, trend_y, color='red', label='Linear Trend')   # Linear trend line
    ax.plot(x, poly_y, color=colors_graph2[2], label='Polynomial Fit', linestyle = '--') # Polynomial trend line

    # set the y limit to include the smoothed data and the trend line
    ax.set_ylim([y_spline.min()*1.10, y_spline.max()*1.10])
    # SPECIFIC USE CASE
    # ax.set_ylim([-0.2, 0.4])

    # Setting the title and labels
    ax.set_title(title, fontsize=20, weight='bold')
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)', fontsize=16, weight='bold')
    ax.set_ylabel('Fold Change', fontsize=16, weight='bold')
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Create custom legend handles
    green_line = mlines.Line2D([], [], color=colors_graph2[1], markersize=15, label='Inward Facing DNA')
    orange_line = mlines.Line2D([], [], color=colors_graph2[0], markersize=15, label='Outward Facing DNA')
    # black_dot = mlines.Line2D([], [], marker='.', markersize=5, color='darkgrey', linestyle='None', label='Original Data')
    blue_line = mlines.Line2D([], [], color=colors_graph2[2], markersize=15, linestyle='--', label='Binomial Fit')

    # Add custom legend handles
    ax.legend(handles=[green_line, orange_line, blue_line],  loc='upper right', fontsize=12,
                   framealpha=0.5, facecolor='white', edgecolor='black', frameon=True, 
                   borderpad=0.2, labelspacing=0.2, handletextpad=0.2)


wt_total = data_frame_operations.DataFormatter.read_dataframe("/home/cam/Documents/AtHomeAnalysis/KBr_treated_proteomutics/KBr_treated.counts")
wt_intersect = data_frame_operations.DataFormatter.read_dataframe("/home/cam/Documents/AtHomeAnalysis/KBr_treated_proteomutics/KBr_treated_non_filtered_TF_map_1000.intersect")

dyads_counts = data_frame_operations.DataFormatter.read_dataframe("/home/cam/Documents/AtHomeAnalysis/non_filtered_TF_map_1000_proteomutics/non_filtered_TF_map_1000.counts")
genomic_counts = data_frame_operations.DataFormatter.read_dataframe('/home/cam/Documents/AtHomeAnalysis/hg19/hg19.counts')

new_dyads_counts = data_frame_operations.DataFormatter.reverse_complement_positional_strand_conversion(dyads_counts)
new_genomic_counts = data_frame_operations.DataFormatter.reverse_complement_tri_counts(genomic_counts)
# new_wt_intersect = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/lesion_files/vcf/SRR_treated_cellular_69-70_proteomutics/SRR_treated_cellular_69-70_hg19_MNase_nucleosome_map_all_flipped.intersect')

data_formatter = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, dyads_counts, genomic_counts, wt_intersect)
# data_formatter2 = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, new_dyads_counts, new_genomic_counts, new_wt_intersect)

# Create a figure and a grid of subplots with 2 rows and 1 column.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

# Use the first Axes (ax1) for the first function and the second Axes (ax2) for the second function.
make_graph_matplotlib(ax1, data_formatter, 'Mutations Across Nucleosomes', smoothing_method='savgol_filter')
make_73_graph_matplotlib(ax2, data_formatter, 'Mutations Within Nucleosomes', smoothing_method='savgol_filter')
# Adjust the layout of the subplots to prevent overlap.
plt.tight_layout()

# Show the plot.
plt.savefig('/home/cam/Documents/AtHomeAnalysis/figures/301_smoothed_tf.svg', format='svg')
plt.show()

with open('/home/cam/Documents/AtHomeAnalysis/ensGeneList_condensed_no_zero.bed') as f, open('/home/cam/Documents/AtHomeAnalysis/ensGeneList_condensed_no_zero_TSS.bed', 'w') as o:
    for line in f:
        line = line.strip().split('\t')
        line[2] = str(int(line[1]) + 1)
        o.write('\t'.join(line) + '\n')