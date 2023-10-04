import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')                                       
from app.utils import data_frame_operations, tools


uv_total = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/UV_nucleomutics/UV.counts')
uv_intersect = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/UV_new.intersect')
dyads_counts = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/dyads_nucleomutics/dyads.counts')
genomic_counts = data_frame_operations.DataFormatter.read_dataframe('backend/test/test_data/hg19.counts')

context_normalized = data_frame_operations.DataFormatter.context_normalization(uv_intersect, dyads_counts)
steve_normalized = data_frame_operations.DataFormatter.genome_wide_normalization(uv_total, dyads_counts, genomic_counts, uv_intersect)


def make_graph_matplotlib(ax, mutation_data: pd.DataFrame, title:str, interpolate_method: bool = False, smoothing_method: None = None):
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    
    x = np.array(indexes)
    y = np.array(graph_values)

    # Your processing with Tools methods
    overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(x, y)

    if smoothing_method:
        x, y = tools.smooth_data(x, y, method=smoothing_method)

    if interpolate_method:
        x, y = tools.interpolate_missing_data(x, y, -1000, 1000, interpolate_method)

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

# make_graph_matplotlib(plt.gca(), context_normalized, 'UV Intersect Context Normalized', interpolate_method='cubic', smoothing_method='moving_average')
make_graph_matplotlib(plt.gca(), context_normalized, 'UV Intersect Context Normalized')
# make_graph_matplotlib(plt.gca(), steve_normalized, 'UV Intersect Genome Wide Normalized', interpolate_method='cubic', smoothing_method='moving_average')
make_graph_matplotlib(plt.gca(), steve_normalized, 'UV Intersect Genome Wide Normalized')

# with open('backend/test/test_data/UV_nucleomutics/test.counts', 'r') as f:
#     for line in f:
#         line = line.strip().split('\t')[1:]
#         print(sum([int(x) for x in line]))



# def count_contexts_mut(file):
#     file = Path(file)
#     total = 0
#     keys = tools.contexts_in_iupac('NNN')
#     counts = {key: 0 for key in keys}
#     with open(file, 'r') as f:
#         for line in f:
#             total += 1
#             tsv = line.strip().split('\t')
#             context = tsv[6]
#             counts[context] += 1
    
#     df = pd.DataFrame(list(counts.items()), columns=['CONTEXTS', 'COUNTS'])

#     df = df.sort_values(by='CONTEXTS')
    
#     df.to_csv(file.with_suffix('.counts'), sep='\t', index=False)
#     print(total)
#     print(df['COUNTS'].sum())

# count_contexts_mut('/media/cam/Working/ProteoMuticsTest/UV_nucleomutics/UV.mut')


