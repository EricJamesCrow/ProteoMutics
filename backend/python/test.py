import MutationIntersector
import Controller
import Graphing
import DataFrameOperations
from pathlib import Path

genome_file = Path('/home/cam/Documents/genome_files/hg19/hg19.fa')
dyad_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/dyads.bed')
mutation_file = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/HMCES_KBr.vcf')

dyad_counts = Path('/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/dyads_hg19_fasta_filtered.counts')


new_sorted_mut_file = Controller.pre_process_mutation_file(mutation_file, genome_file)
new_dyad_file = Controller.pre_process_nucleosome_map(dyad_file, genome_file)

intersector = MutationIntersector.MutationIntersector(mutation_file = new_sorted_mut_file, dyad_file = dyad_file, output_file= mutation_file.with_suffix('.intersect'))
intersected_file = intersector.output_file

df = DataFrameOperations.format_dataframe(intersected_file, dyad_counts=dyad_counts, iupac='NNN', count_complements=False, normalize_to_median=True, z_score_filter=None)

graphing_data = Graphing.make_graph(df, interpolate_method='cubic', smoothing_method='moving_average')
fig, period, confidence, signal_to_noise = graphing_data

Graphing.save_figure(fig, dpi=300, fig_output_name='test.png')