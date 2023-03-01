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

