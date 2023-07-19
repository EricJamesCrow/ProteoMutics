import MutationIntersector
import Controller
from pathlib import Path

genome_file = Path('/home/cam/Documents/genome_files/hg19/hg19.fa')
dyad_file = Path('/media/cam/Data9/8-oxodG_Final_Analysis/nucleosome/dyads.bed')
mutation_file = Path('/media/cam/Data9/8-oxodG_Final_Analysis/vcf_files/KBr_treated.vcf')
sorted_mut_file = '/media/cam/Data9/8-oxodG_Final_Analysis/vcf_files/KBr_treated_nucleomutics/KBr_treated.mut'


Controller.pre_process_mutation_file(mutation_file, genome_file)

MutationIntersector.MutationIntersector(mutation_file = sorted_mut_file, dyad_file = dyad_file, output_file= '/media/cam/Data9/8-oxodG_Final_Analysis/vcf_files/KBr_treated_nucleomutics/KBr_treated.intersect')