from pathlib import Path
import pandas as pd

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

