from pathlib import Path
import pandas as pd
import subprocess
import BedtoolsCommands
import Tools

def adjust_dyad_positions(dyad_file: Path):
    """Takes a dyad file with single nucleotide positions and creates a new bed file with -500 and +500 positions

    Args:
        dyad_file (.bed): A dyad map that has the dyad (center) position of the nucleosome in a bed3 format
    """
    
    # Create the new filename
    output_file = dyad_file.with_stem(dyad_file.stem + '_plus-minus_1000')

    # Use a with statement to read and write to the files
    with open(dyad_file, 'r') as f, open(output_file, 'w') as o:
        
        # Loop through the lines in the input file and expand the positions by 500 on either side
        for line in f:
            tsv = line.strip().split()
            new_start = str(int(tsv[1]) - 1001)
            new_end = str(int(tsv[2]) + 1001)
            new_line_values = [tsv[0], new_start, new_end] + tsv[3:]
            o.write('\t'.join(new_line_values) + '\n')

def filter_lines_with_n(dyad_fasta: Path, dyad_bed: Path):
    # Filter lines and write to new files
    with open(dyad_fasta, 'r') as fa, open(dyad_bed, 'r') as bed, \
         open(dyad_fasta.with_stem(f'{dyad_fasta.stem}_filtered'), 'w') as new_fa, \
         open(dyad_bed.with_stem(f'{dyad_bed.stem}_filtered'), 'w') as new_bed:
        for fa_line, bed_line in zip(fa, bed):
            if 'N' not in fa_line:
                new_fa.write(fa_line)
                new_bed.write(bed_line)

def check_and_sort(input_file: Path):
    # PLACE CHECK CODE HERE WITH -c METHOD
    sorted_name = input_file.with_stem(f'{input_file.stem}_sorted')
    command = f'sort -k1,1 -k2,2 -k3,3 -k6,6 {input_file} > {sorted_name}'
    with subprocess.Popen(args=command, stdout=subprocess.PIPE, shell=True) as p:
        return p, sorted_name
    
def filter_acceptable_chromosomes(input_file: Path, genome: str):
    human = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X']
    output_file = input_file.with_stem(input_file.stem+'_filtered')
    if genome == 'human':
        with open(input_file, 'r') as f, open(output_file, 'w') as o:
            for line in f:
                chrom = line.strip().split('\t')[0][3:]
                if chrom in human:
                    o.write(line)

def vcf_snp_to_intermediate_bed(vcf_file: Path):
    intermediate_bed = vcf_file.with_suffix('.tmp')
    with open(vcf_file) as f, open(intermediate_bed, 'w') as o:
        for line in f:
            if line[0] == '#': continue
            if 'CHROM' in line:
                header = line
                continue
            tsv = line.strip().split('\t')
            if not (len(tsv[3]) == 1 and len(tsv[4]) == 1 and tsv[3] in 'ACGT' and tsv[4] in 'ACGT'): continue
            chrom = tsv[0]
            base_0 = str(int(tsv[1])-2)
            base_1 = str(int(tsv[1])+1)
            name = '.'
            score = '0'
            strand = '+'
            mutation_type = f'{tsv[3]}>{tsv[4]}'
            new_line = '\t'.join([chrom, base_0, base_1, name, score, strand, mutation_type])
            o.write(new_line+'\n')

def expand_context_custom_bed(intermediate_bed: Path, fasta_file: Path):
    bed_file = intermediate_bed.with_suffix('.bed')
    _, getfasta_output = BedtoolsCommands.bedtools_getfasta(intermediate_bed, fasta_file)
    with open(getfasta_output) as f, open(intermediate_bed) as i, open(bed_file, 'w') as o:
        for fasta_line, bed_line in zip(f, i):
            fasta_context = fasta_line.strip().split('\t')[-1]
            bed_info = bed_line.strip().split('\t')
            new_line = '\t'.join([bed_info[0], str(int(bed_info[1])+1), str(int(bed_info[2])-1), bed_info[3], bed_info[4], bed_info[5], fasta_context.upper(), bed_info[6]])
            o.write(new_line+'\n')


