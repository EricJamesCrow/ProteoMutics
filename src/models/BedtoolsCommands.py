import subprocess
from pathlib import Path

def bedtools_getfasta(dyad_file: Path, fasta_file: Path):
    """runs `bedtools getfasta` on the input dyad file and returns fasta file

    Args:
        dyad_file (Path): .bed file with +/- 500 generated from General.py/adjust_dyad_positions()\n
        fasta_file (Path): .fa file that is the genome fasta file associated with the dyad positions (ex: hg19.fa)
    """

    # creates a name for the new file with a .fa ending
    output_fasta_file = dyad_file.with_suffix('.fa')
    
    # runs the bedtools getfasta tool given the input files
    with subprocess.Popen(  args=[f'bedtools getfasta -fi {fasta_file} -bed {dyad_file} -fo {output_fasta_file} -tab'], stdout=subprocess.PIPE,
                            shell=True) as p:
        return p, output_fasta_file

def bedtools_intersect(mutation_file: Path, expanded_dyad_file: Path):
    """runs `bedtools intersect` using `mutation_file` and `expanded_dyad_file` and returns a tab separated file showing the intersections.

    Args:
        mutation_file (Path): .bed file with mutations in any format, as long as the first columns are bed3\n
        dyad_file (Path): .bed file with expanded dyad positions in any format, as long as the first columns are bed3
    """

    # creates a name for the new file with a .fa ending
    intersect_file = mutation_file.with_suffix('.txt').with_stem(f'{mutation_file.stem}_{expanded_dyad_file.stem}_intersect')
    
    # runs the bedtools intersect with the given files and outputs both files into the intersect using the -wa -wb options
    with subprocess.Popen(  args=[f'bedtools intersect -wa -wb -a {mutation_file} -b {expanded_dyad_file} > {intersect_file}'], stdout=subprocess.PIPE,
                            shell=True) as p:
        return p, intersect_file