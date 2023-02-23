import BedtoolsCommands
import Statistics
import General
import Tools
from pathlib import Path
import multiprocessing as mp
import pandas as pd
from plotnine import *
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# General.adjust_dyad_positions(
#     dyad_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads.bed')
# )

# BedtoolsCommands.bedtools_getfasta(
#     dyad_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500.bed'),
#     fasta_file=Path('/media/cam/Data9/CortezAnalysis/pipeline_files/hg19.fa')
# )

# BedtoolsCommands.bedtools_intersect(
#     mutation_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/Analysis/vcf_files/concat/KM_treated.bed'),
#     expanded_dyad_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500.bed')
# )

# if __name__ == '__main__':
#     mp.freeze_support()
#     fasta_counter = Statistics.DyadFastaCounter(Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500.fa'))
#     fasta_counter.run()


###################################################33 plotnine graph code ##################################33
# position_list = (General.mutation_position(
#     intersect_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_69-70_sorted_dyads_plus-minus_500_intersect.txt')
# ))
# mut_counter = Statistics.MutationCounter(
#     intersect_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_69-70_sorted_dyads_plus-minus_500_intersect.txt')
# )
# position_list = mut_counter.run()
# df = pd.DataFrame(position_list, index = range(-500,501), columns=['counts'])
# normalization_factors = Statistics.g_only_normalize_counts()
# normalized_list = [position_list[i] / normalization_factors[i] for i in range(len(position_list))]
# df = pd.DataFrame(normalized_list, index =range(-500, 501), columns =['normalized_values'])
# df.to_csv('Mutations_normalized_df.txt', sep = '\t')
# df = pd.read_csv('/home/cam/Documents/repos/Nucleomutics/WT_normalized_df.txt', sep='\t')
# p = ggplot(df, aes(x='index', y='normalized_values')) + \
#     geom_line() + \
#     scale_y_continuous(limits=(np.percentile(df['normalized_values'], 1), np.percentile(df['normalized_values'], 99))) + \
#     xlab('nucleosome_position') + \
#     ylab('value') + \
#     ggtitle('WT')

# Convert the plot to a matplotlib plot object
# p.save('WT_nucleosome.png')
# fig = p.draw()
# ax = fig.gca()

# Display the plot using matplotlib
# plt.show()

# df = pd.read_csv('/home/cam/Documents/repos/Nucleomutics/WT_normalized_df.txt', sep='\t', header=0, index_col=0)
df = pd.read_csv('VITRO_normalized_df.txt', index_col=0, header=0, sep = '\t')
df = df[(np.abs(stats.zscore(df['normalized_values'])) <3)]
# # df.to_csv('Mutations_normalized.tsv', sep = '\t')


x = df['index'].to_numpy()
y = df['normalized_values'].to_numpy()

smoothed_x, smoothed_y = Tools.smooth_data(x,y)
# print(smoothed_data)

# Create the scatter plot with smaller dots
fig, ax = plt.subplots()
ax.scatter(x, y, s=5)
ax.plot(smoothed_x, smoothed_y, 'r-', lw = 2)

# Set the x-axis and y-axis labels
ax.set_xlabel('X values')
ax.set_ylabel('Y values')

# Set the title of the plot
ax.set_title('Scatter Plot')

# Disable scientific notation on the x-axis
ax.ticklabel_format(axis='x', style='plain')

# Format y-axis tick labels as whole numbers
formatter = plt.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x))
ax.yaxis.set_major_formatter(formatter)

# Set the number of ticks on the y-axis
ax.yaxis.set_major_locator(plt.MaxNLocator(5))

# Display the plot
# plt.savefig('/home/cam/Documents/repos/Nucleomutics/Mutations_nucleosome.png', dpi = 300)
plt.show()
