import BedtoolsCommands
import models.DataFrameOperations as DataFrameOperations
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

df = DataFrameOperations.df_division_and_standardization(
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_69-70_adjusted_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_67-68_adjusted_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_64-65-66_adjusted_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    mutation_counts=Path('/home/cam/Documents/UV_Data/MELA-AU_trinuc_context_mutations_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    # mutation_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/Analysis/vcf_files/concat/KM_treated_filtered_sorted_dyads_filtered_sorted_intersected_mutations_counts.txt'),
    dyad_counts=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_1000_hg19_fasta_filtered_counts.txt'),
    iupac = 'NCN'
    )

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

smoothed_x, smoothed_y = Tools.smooth_data(x,y)
# print(smoothed_data)

# Create the scatter plot with smaller dots
nucleosome_start = int(len(smoothed_x)/2)-73
nucleosome_end = int(len(smoothed_x)/2)+73
fig, ax = plt.subplots()
ax.scatter(x, y, marker='.', s=1, linewidths=1)
ax.plot(smoothed_x, smoothed_y, 'b-', lw = 2)
ax.plot(smoothed_x[nucleosome_start:nucleosome_end], smoothed_y[nucleosome_start:nucleosome_end], 'r-', lw = 2)

data = Tools.find_periodicity(x[927:1073], y[927:1073], 10.7)
print(data)

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
