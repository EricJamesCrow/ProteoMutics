from pathlib import Path

def adjust_dyad_positions(input_file: Path):
    """Takes a dyad file with single nucleotide positions and creates a new bed file with -500 and +500 positions

    Args:
        input_file (.bed): A dyad map that has the dyad (center) position of the nucleosome in a bed3 format
    """
    
    # opens the input file with i/o
    with open(input_file, 'r') as f:
        
        # creates the new filename and opens it
        output_file = input_file.with_stem(input_file.stem+'plus-minus_500')
        with open(output_file, 'w') as o:
            
            # expands the positions by 500 on either side
            for line in f:
                tsv = line.strip().split()
                new_start = str(int(tsv[1])-500)
                new_end = str(int(tsv[2])+500)
                new_line_values = [tsv[0]]+[new_start,new_end]+[tsv[3:]]
                o.write('\t'.join(new_line_values)+'\n')


