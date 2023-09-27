import MutationIntersector
import Controller
import Graphing
import DataFrameOperations
from pathlib import Path

genome_file = Path('/home/cam/Documents/genome_files/hg19/hg19.fa')
dyad_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/dyads.bed')
mutation_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/HMCES_KBr.vcf')
intersected_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/HMCES_KBr_nucleomutics/HMCES_KBr_dyads_intersected_mutations_counts.txt')
dyad_counts = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/dyads_nucleomutics/dyads_hg19_fasta_filtered.counts')


# new_sorted_mut_file = Controller.pre_process_mutation_file(mutation_file, genome_file)
# new_dyad_file = Controller.pre_process_nucleosome_map(dyad_file, genome_file)

# intersector = MutationIntersector.MutationIntersector(mutation_file = new_sorted_mut_file, dyad_file = dyad_file, output_file= mutation_file.with_suffix('.intersect'))
# intersected_file = intersector.output_file

df = DataFrameOperations.format_dataframe(intersected_file, dyad_counts=dyad_counts, iupac='NNN', normalize_to_tri=True, count_complements=False, normalize_to_median=True, z_score_filter=2.5)
df.to_csv(intersected_file.with_name('data_df.txt'), sep='\t', index=True, header=True)

import pandas as pd

df = '/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/HMCES_KBr_nucleomutics/data_df.txt'
df = pd.read_csv(df, sep='\t', index_col=0, header=0)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import Tools
# Assuming you've already defined or imported the Tools class/methods elsewhere in your script.

def make_graph_matplotlib(mutation_data: pd.DataFrame, interpolate_method: bool = False, smoothing_method: None = None):
    
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    
    x = np.array(indexes)
    y = np.array(graph_values)
    
    # Your processing with Tools methods (keep this unchanged)
    period, confidence, signal_to_noise = Tools.find_periodicity(x, y, 10.2)
    overall_period, overall_confidence, overall_signal_to_noise = Tools.find_periodicity(x, y, 300)
    
    if smoothing_method:
        x, y = Tools.smooth_data(x, y, method=smoothing_method)
    
    if interpolate_method:
        x, y = Tools.interpolate_missing_data(x, y, -1000, 1000, interpolate_method)

    # Define the x-domain of interest for the nucleosome
    xmin = -73
    xmax = 73

    # Set up the Matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(10,6))
    
    # Plot the scatter points in black
    ax.scatter(x, y, c='black', s=2)

    # Plot colored line segments
    for i in range(1, len(x)):
        if xmin <= x[i-1] <= xmax and xmin <= x[i] <= xmax:
            ax.plot(x[i-1:i+1], y[i-1:i+1], color='red')
        else:
            ax.plot(x[i-1:i+1], y[i-1:i+1], color='blue')

    # Set the title and labels
    ax.set_title('Nucleomutics!')
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
    ax.set_ylabel('Mutation Counts Normalized to Context')
    
    # Display the plot
    plt.show()

    # Return your other values
    return period, confidence, signal_to_noise

result = make_graph_matplotlib(df, interpolate_method='linear')
result = make_graph_matplotlib(df, interpolate_method='linear', smoothing_method='moving_average')
