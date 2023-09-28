import MutationIntersector
import Controller
import Graphing
import FastaCounter
import DataFrameOperations
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import Tools
import DyadContextCounter

print('Imported modules.')
genome_file = Path('/home/cam/Documents/genome_files/hg19/hg19.fa')
dyad_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/dyads.bed')
mutation_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/HMCES_KBr.vcf')
# intersected_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/HMCES_KBr_nucleomutics/HMCES_KBr_dyads_intersected_mutations_counts.txt')
dyad_counts = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/dyads_nucleomutics/dyads_hg19_fasta_filtered.counts')
uv_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/UV_nucleomutics/UV.mut')
# hg19_counts = Path('/home/cam/Documents/genome_files/hg19/hg19_3mer.counts')

# print('Pre-processing fasta file...')
# FastaCounter.GenomeFastaCounter(genome_file, 3)
# print('Pre-processing dyad file...')
Controller.pre_process_nucleosome_map(dyad_file, genome_file)
# print('Counting dyad contexts...')
# counter = DyadContextCounter.DyadFastaCounter(dyad_file)
# counter.run()
print('Intersecting mutation file...')
intersected_file = MutationIntersector.MutationIntersector(mutation_file = uv_file, dyad_file = dyad_file) # mutation_type='C>T', mut_context='YCY')
intersected_file.run()

# print('Formatting dataframe...')
# df = DataFrameOperations.DataFormatter(intersected_file, dyad_counts=dyad_counts, iupac='NNN', context_normalize=True, count_complements=False, normalize_to_median=True, z_score_filter=None)
# print('Making graph...')
# def make_graph_matplotlib(mutation_data: pd.DataFrame, interpolate_method: bool = False, smoothing_method: None = None):
    
#     indexes = mutation_data.index.tolist()
#     graph_values = []
#     for item in indexes:
#         graph_values.append(sum(mutation_data.loc[item]))
    
#     x = np.array(indexes)
#     y = np.array(graph_values)

#     # Your processing with Tools methods (keep this unchanged)
#     overall_period, overall_confidence, overall_signal_to_noise = Tools.find_periodicity(x, y)

#     if smoothing_method:
#         x, y = Tools.smooth_data(x, y, method=smoothing_method)

#     if interpolate_method:
#         x, y = Tools.interpolate_missing_data(x, y, -1000, 1000, interpolate_method)


#     # Identify peaks based on overall_period
#     peaks = [0]  # first peak is at 0

#     # Handle right side of the graph
#     while peaks[-1] + overall_period < x[-1]:
#         peaks.append(peaks[-1] + overall_period)

#     # Handle left side of the graph
#     while peaks[0] - overall_period > x[0]:
#         peaks.insert(0, peaks[0] - overall_period)

#     # Define a function to check if a value is within a red region
#     def in_red_region(val):
#         for peak in peaks:
#             if peak - 73 <= val <= peak + 73:
#                 return True
#         return False

#     # Set up the Matplotlib figure and axis
#     fig, ax = plt.subplots(figsize=(10,6))

#     # Plot the scatter points in black
#     ax.scatter(x, y, c='black', s=2)

#     # Plot colored line segments
#     for i in range(1, len(x)):
#         if in_red_region(x[i-1]) and in_red_region(x[i]):
#             ax.plot(x[i-1:i+1], y[i-1:i+1], color='red')
#         else:
#             ax.plot(x[i-1:i+1], y[i-1:i+1], color='blue')

#     # Set the title and labels
#     ax.set_title('Proteomutics!')
#     ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
#     ax.set_ylabel('Mutation Counts Normalized to Context')

#     # Display the plot
#     plt.show()

#     # Return your other values
#     return overall_period, overall_confidence, overall_signal_to_noise

# result = make_graph_matplotlib(df, interpolate_method='linear')
# result = make_graph_matplotlib(df, interpolate_method='linear', smoothing_method='moving_average')
# print(result)
