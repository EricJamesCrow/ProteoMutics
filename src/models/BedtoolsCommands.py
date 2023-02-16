import subprocess
from pathlib import Path

def bedtools_getfasta_dyad(input_file: Path, fasta_file: Path):
    """runs `bedtools getfasta` on the input dyad file and returns fasta file

    Args:
        input_file (.bed): The +/- 500 .bed file generated from General.py/adjust_dyad_positions()
        fasta_file (.fa): The genome fasta file associated with the dyad positions (ex: hg19.fa)
    """
    # creates a name for the new file with a .fa ending
    dyad_fasta_file = input_file.with_suffix('.fa')
    
    # 
    with subprocess.Popen(  args=[f'bedtools getfasta -fi {fasta_file} -bed {input_file} -fo {dyad_fasta_file} -tab'], stdout=subprocess.PIPE,
                            shell=True) as p:
            for text in p.stdout:
                print(text)