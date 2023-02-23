from pathlib import Path
import multiprocessing as mp

def adjust_dyad_positions(dyad_file: Path):
    """Takes a dyad file with single nucleotide positions and creates a new bed file with -500 and +500 positions

    Args:
        dyad_file (.bed): A dyad map that has the dyad (center) position of the nucleosome in a bed3 format
    """
    
    # Create the new filename
    output_file = dyad_file.with_stem(dyad_file.stem + '_plus-minus_500')

    # Use a with statement to read and write to the files
    with open(dyad_file, 'r') as f, open(output_file, 'w') as o:
        
        # Loop through the lines in the input file and expand the positions by 500 on either side
        for line in f:
            tsv = line.strip().split()
            new_start = str(int(tsv[1]) - 500)
            new_end = str(int(tsv[2]) + 500)
            new_line_values = [tsv[0], new_start, new_end] + tsv[3:]
            o.write('\t'.join(new_line_values) + '\n')

# parallelize this tomorrow using blocks
def mutation_position(intersect_file: Path):
    with open(intersect_file, 'r') as f:
        # Read the first line of the file to get the column names
        header = f.readline().strip().split('\t')
        # Find the index of any string that contains the substring "chr"
        chr_positions = [i for i, col in enumerate(header) if 'chr' in col]
        mutation_file_start = chr_positions[0]+1
        dyad_file_start = chr_positions[1]+1
        f.seek(0)
        mutations_dyad = [0 for _ in range(1001)]
        for line in f:
            tsv = line.strip().split('\t')
            mutations_dyad[int(tsv[dyad_file_start])-int(tsv[mutation_file_start])] += 1
        return(mutations_dyad)





