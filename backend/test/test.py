import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')                                       
from app.utils import data_frame_operations, tools


wt_total = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/hmces/vcf_files/genotype_split/HMCES_KBr_proteomutics/HMCES_KBr.counts')
wt_intersect = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/hmces/vcf_files/genotype_split/HMCES_KBr_proteomutics/HMCES_KBr_hg19_MNase_nucleosome_map_all.intersect')
dyads_counts = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/ProteoMuticsTest/hg19_MNase_nucleosome_map_all_proteomutics/hg19_MNase_nucleosome_map_all.counts')
genomic_counts = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/ProteoMuticsTest/hg19.counts')

new_dyads_counts = data_frame_operations.DataFormatter.reverse_complement_positional_strand_conversion(dyads_counts)
new_genomic_counts = data_frame_operations.DataFormatter.reverse_complement_tri_counts(genomic_counts)
new_wt_intersect = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/hmces/vcf_files/genotype_split/HMCES_KBr_proteomutics/HMCES_KBr_hg19_MNase_nucleosome_map_all_flipped.intersect')

data_formatter = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, dyads_counts, genomic_counts, wt_intersect)
data_formatter2 = data_frame_operations.DataFormatter.genome_wide_normalization(wt_total, new_dyads_counts, new_genomic_counts, new_wt_intersect)

def make_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, interpolate_method: bool = False, smoothing_method: None = None):
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    
    x = np.array(indexes)
    y = np.array(graph_values)


    # if smoothing_method:
    #     x, y = tools.smooth_data(x, y, method=smoothing_method, window_size=55, poly_order=3)

    if interpolate_method:
        x, y = tools.interpolate_missing_data(x, y, -1000, 1000, interpolate_method)

    # Your processing with Tools methods
    overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(x, y)

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

    # plt.show()


def make_73_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, smoothing_method):
    # Filter the data for the desired range (-72 to +72)
    mutation_data = mutation_data[(mutation_data.index >= -65) & (mutation_data.index <= 65)]

    # Now, the 'indexes' will only contain values from -72 to +72
    indexes = mutation_data.index.tolist()
    graph_values = [sum(mutation_data.loc[item]) for item in indexes]
    
    x = np.array(indexes)
    y = np.array(graph_values)

    if smoothing_method:
        x, y = tools.smooth_data(x, y, method=smoothing_method, window_size=7, poly_order=3)

    # No smoothing or interpolation applied, so we can skip the related conditions

    # We'll directly plot the data without considering peaks or red regions,
    # as we're focusing on a specific section of the data.

    # Plotting on the passed ax
    ax.scatter(x, y, c='black', s=2)  # This creates the scatter plot
    ax.plot(x, y, color='blue')  # This creates a blue line connecting the points

    # Setting the title and labels
    ax.set_title(title)
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
    ax.set_ylabel('Mutation Counts Normalized to Context')

    # plt.show()  # Make sure to display the plot

# make_graph_matplotlib(plt.gca(), data_formatter, 'WT Dyads', smoothing_method='moving_average')
# make_73_graph_matplotlib(plt.gca(), data_formatter2, 'WT Dyads', smoothing_method='moving_average')
# make_graph_matplotlib(plt.gca(), data_formatter2, 'WT Dyads Flipped')

# Create a figure and a grid of subplots with 2 rows and 1 column.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Use the first Axes (ax1) for the first function and the second Axes (ax2) for the second function.
make_graph_matplotlib(ax1, data_formatter, 'WT Dyads', smoothing_method='savgol_filter')
make_73_graph_matplotlib(ax2, data_formatter, 'WT Dyads 73', smoothing_method='savgol_filter')
# Adjust the layout of the subplots to prevent overlap.
plt.tight_layout()

# Show the plot.
plt.show()