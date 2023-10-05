import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')                                       
from app.utils import data_frame_operations, tools


uv_total = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/UV_nucleomutics/UV.counts')
uv_intersect = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/UV_nucleomutics/UV_dyads.intersect')
dyads_counts = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/dyads_nucleomutics/dyads.counts')
genomic_counts = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/hg19.counts')

new_dyads_counts = data_frame_operations.DataFormatter.reverse_complement_positional_strand_conversion(dyads_counts)
new_genomic_counts = data_frame_operations.DataFormatter.reverse_complement_tri_counts(genomic_counts)
new_uv_intersect = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/UV_nucleomutics/UV_dyads_flipped.counts')

data_formatter = data_frame_operations.DataFormatter.genome_wide_normalization(uv_total, new_dyads_counts, new_genomic_counts, uv_intersect)
data_formatter2 = data_frame_operations.DataFormatter.genome_wide_normalization(uv_total, new_dyads_counts, new_genomic_counts, new_uv_intersect)

whole_genome = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/UV_nucleomutics/UV_hg19_MNase_nucleosome_map_all.intersect')
whole_genome_flipped = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/UV_nucleomutics/UV_hg19_MNase_nucleosome_map_all_flipped.counts')

whole_genome_dyad = data_frame_operations.DataFormatter.read_dataframe('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/hg19_MNase_nucleosome_map_all_nucleomutics/hg19_MNase_nucleosome_map_all.counts')

data_formatter3 = data_frame_operations.DataFormatter.genome_wide_normalization(uv_total, whole_genome_dyad, new_genomic_counts, whole_genome)
data_formatter4 = data_frame_operations.DataFormatter.genome_wide_normalization(uv_total, whole_genome_dyad, new_genomic_counts, whole_genome_flipped)

def make_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, interpolate_method: bool = False, smoothing_method: None = None):
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    
    x = np.array(indexes)
    y = np.array(graph_values)


    if smoothing_method:
        x, y = tools.smooth_data(x, y, method=smoothing_method)

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

    plt.show()

# make_graph_matplotlib(plt.gca(), data_formatter, 'UV Dyads')
# make_graph_matplotlib(plt.gca(), data_formatter2, 'UV Dyads Flipped')
# make_graph_matplotlib(plt.gca(), data_formatter3, 'UV Whole Genome')
# make_graph_matplotlib(plt.gca(), data_formatter4, 'UV Whole Genome Flipped')