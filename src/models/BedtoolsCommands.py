import subprocess
from pathlib import Path

def bedtools_getfasta(dyad_file: Path, fasta_file: Path):
    """Runs `bedtools getfasta` on the input dyad file and returns fasta file.

    Args:
        dyad_file (Path): .bed file with +/- 500 generated from General.adjust_dyad_positions().
        fasta_file (Path): .fa file that is the genome fasta file associated with the dyad positions (ex: hg19.fa).
    """
    # Create a name for the new file with a .fa ending
    output_fasta_file = dyad_file.with_suffix('.fa').with_stem(f'{dyad_file.stem}_{fasta_file.stem}_fasta')

    # Run the bedtools getfasta tool given the input files
    command = f'bedtools getfasta -fi {fasta_file} -bed {dyad_file} -fo {output_fasta_file} -tab'
    with subprocess.Popen(args=command, stdout=subprocess.PIPE, shell=True) as p:
        return p, output_fasta_file

def bedtools_intersect(mutation_file: Path, expanded_dyad_file: Path):
    """Runs `bedtools intersect` using `mutation_file` and `expanded_dyad_file` and returns a tab separated file showing the intersections.

    Args:
        mutation_file (Path): .bed file with mutations in any format, as long as the first columns are bed3.
        dyad_file (Path): .bed file with expanded dyad positions in any format, as long as the first columns are bed3.
    """
    # Create a name for the new file with a .txt ending
    intersect_file = mutation_file.with_suffix('.txt').with_stem(f'{mutation_file.stem}_{expanded_dyad_file.stem}_intersect')

    # Run the bedtools intersect with the given files and output both files into the intersect using the -wa -wb options
    command = f'bedtools intersect -wa -wb -a {mutation_file} -b {expanded_dyad_file} > {intersect_file}'
    result = subprocess.run(command, shell=True, check=True)
    return intersect_file

