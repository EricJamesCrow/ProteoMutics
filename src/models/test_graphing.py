import BedtoolsCommands
import DataFrameOperations
import General
import Tools
from pathlib import Path
import multiprocessing as mp
import pandas as pd
from plotnine import *
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

###################################################33 plotnine graph code ##################################33

df = DataFrameOperations.format_dataframe(
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_69-70_adjusted_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_67-68_adjusted_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_64-65-66_adjusted_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    mutation_counts=Path('/home/cam/Documents/UV_Data/MELA-AU_trinuc_context_mutations_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/Analysis/vcf_files/concat/KM_treated_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    # dyad_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_1000_hg19_fasta_filtered_counts.txt'),
    normalize_to_median=False)

# df = Statistics.df_just_raw_counts(
#     mutation_counts = Path('/home/cam/Documents/UV_Data/MELA-AU_trinuc_context_mutations_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'), 
#     iupac='NCN'
#     )

df = df[(np.abs(stats.zscore(df)) < 3).all(axis=1)]

indexes = df.index.tolist()
graph_values = []
for item in indexes:
    graph_values.append(sum(df.loc[item]))
x = np.array(indexes)
y = np.array(graph_values)

smoothed_x, smoothed_y = Tools.smooth_data(x, y)

fig, ax = plt.subplots()
ax.scatter(x, y, marker='.', s=1, linewidths=1)
x_all, y_all = Tools.interpolate_missing_data(smoothed_x, smoothed_y, -1000, 1000)
# Define the x-domain of interest
xmin = -73
xmax = 73
# Create a mask to select the x-values in the specified domain
mask = (x_all >= xmin) & (x_all <= xmax)

# Plot the line segments connecting each data point in the domain
for i in range(len(x_all)-1):
    if mask[i] and mask[i+1]:
        ax.plot([x_all[i], x_all[i+1]], [y_all[i], y_all[i+1]], color='red', lw=2)

# Plot the line segments for the outer domain
outer_minus_mask = (x_all <= xmin)
outer_plus_mask = (x_all >= xmax)
for i in range(len(x_all)-1):
    if outer_minus_mask[i] and outer_minus_mask[i+1]:
        ax.plot([x_all[i], x_all[i+1]], [y_all[i], y_all[i+1]], color='blue', lw=2)
    if outer_plus_mask[i] and outer_plus_mask[i+1]:
        ax.plot([x_all[i], x_all[i+1]], [y_all[i], y_all[i+1]], color='blue', lw=2)

# Set the x-axis and y-axis labels
ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
ax.set_ylabel('Mutation Counts Normalized to Context')

# Set the title of the plot
ax.set_title('Nucleomutics?')

# Disable scientific notation on the x-axis
ax.ticklabel_format(axis='x', style='plain')

# Display the plot
# plt.savefig('/home/cam/Documents/repos/Nucleomutics/Mutations_nucleosome.png', dpi = 300)

# add gridlines
ax.grid(True)

plt.show()
