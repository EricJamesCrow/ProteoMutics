from pathlib import Path

def position_percentages_in_dyad(dyad_fasta_file: Path):
    with open(dyad_fasta_file, 'r') as f:
        