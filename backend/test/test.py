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
from matplotlib.collections import LineCollection


def make_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, interpolate_method: bool = False, smoothing_method: None = None):
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    
    x = np.array(indexes)
    y = np.array(graph_values)


    if smoothing_method:
        x, y = tools.smooth_data(x, y, method=smoothing_method, window_size=55, poly_order=3)
        # x_smooth, y_smooth = tools.smooth_data(x, y, method=smoothing_method, window_size=55, poly_order=3)
        # spline = make_interp_spline(x_smooth, y_smooth, k=3)
        # x_spline = np.linspace(x_smooth.min(), x_smooth.max(), 500)
        # y_spline = spline(x_spline)
        # ax.plot(x_spline, y_spline, color='green', label='Smoothed Curve')

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

def make_73_graph_matplotlib(ax, mutation_data: pd.DataFrame, title: str, smoothing_method):
    # Filter the data for the desired range (-72 to +72)
    mutation_data = mutation_data[(mutation_data.index >= -72) & (mutation_data.index <= 72)]

    # Extract the indexes and values from the data frame
    indexes = mutation_data.index.tolist()
    graph_values = [sum(mutation_data.loc[item]) for item in indexes]

    x = np.array(indexes)
    y = np.array(graph_values)

    # Assuming 'tools.find_periodicity' gives you the overall period
    overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(x, y, min_period=2, max_period=30)
    print(f"Overall period: {overall_period}, confidence: {overall_confidence}, signal to noise: {overall_signal_to_noise}")
    half_period = overall_period / 2

    # Perform smoothing if specified
    if smoothing_method:
        x_smooth, y_smooth = tools.smooth_data(x, y, method=smoothing_method, window_size=5, poly_order=3)

        # Manually determine expected peak positions
        expected_peaks = [i for i in range(int(x_smooth.min()), int(x_smooth.max()), int(overall_period))]

        # Find the actual peaks in the smoothed data
        peaks, _ = find_peaks(y_smooth, distance=half_period)
        # Filter peaks that are within a 5 bp window of expected peaks
        actual_peaks = [peak for peak in peaks if any(abs(peak - exp_peak) <= 5 for exp_peak in expected_peaks)]

        # Color the graph based on inward/outward facing DNA
        for peak in actual_peaks:
            # Define the region around the peak as inward facing (blue)
            start_inward = max(0, peak - int(half_period))
            end_inward = min(len(x_smooth) - 1, peak + int(half_period))
            ax.plot(x_smooth[start_inward:end_inward], y_smooth[start_inward:end_inward], color='blue', linewidth=2)

    # Plot the entire smooth line (if smoothing was done) in black as the background
    ax.plot(x_smooth, y_smooth, color='black', linewidth=1, label='Smoothed Data')

    # Label outward facing regions (not covered by peaks) as green
    outward_mask = np.ones(len(y_smooth), dtype=bool)
    for peak in actual_peaks:
        start_inward = max(0, peak - int(half_period))
        end_inward = min(len(y_smooth) - 1, peak + int(half_period))
        outward_mask[start_inward:end_inward] = False

    ax.plot(x_smooth[outward_mask], y_smooth[outward_mask], color='green', linewidth=2)

    # Add a custom legend for the colors
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='black', lw=1, label='Background'),
        Line2D([0], [0], color='green', lw=2, label='Outward Facing DNA'),
        Line2D([0], [0], color='blue', lw=2, label='Inward Facing DNA'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Setting the title and labels
    ax.set_title(title)
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
    ax.set_ylabel('Mutation Counts Normalized to Context')


wt_total = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/lesion_files/vcf/SRR_treated_cellular_69-70_proteomutics/SRR_treated_cellular_69-70.counts')
wt_intersect = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/lesion_files/vcf/SRR_treated_cellular_69-70_proteomutics/SRR_treated_cellular_69-70_hg19_MNase_nucleosome_map_all.intersect')

dyads_counts = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/ProteoMuticsTest/hg19_MNase_nucleosome_map_all_proteomutics/hg19_MNase_nucleosome_map_all.counts')
genomic_counts = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/ProteoMuticsTest/hg19.counts')

new_dyads_counts = data_frame_operations.DataFormatter.reverse_complement_positional_strand_conversion(dyads_counts)
new_genomic_counts = data_frame_operations.DataFormatter.reverse_complement_tri_counts(genomic_counts)
new_wt_intersect = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/lesion_files/vcf/SRR_treated_cellular_69-70_proteomutics/SRR_treated_cellular_69-70_hg19_MNase_nucleosome_map_all_flipped.intersect')

data_formatter = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, dyads_counts, genomic_counts, wt_intersect)
data_formatter2 = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, new_dyads_counts, new_genomic_counts, new_wt_intersect)

# Create a figure and a grid of subplots with 2 rows and 1 column.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Use the first Axes (ax1) for the first function and the second Axes (ax2) for the second function.
make_graph_matplotlib(ax1, data_formatter, 'WT Dyads', smoothing_method='savgol_filter')
make_73_graph_matplotlib(ax2, data_formatter, 'WT Dyads 73', smoothing_method='savgol_filter')
# Adjust the layout of the subplots to prevent overlap.
plt.tight_layout()

# Show the plot.
plt.show()
