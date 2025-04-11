import subprocess
import pandas as pd
import multiprocessing as mp
from pathlib import Path
import sys
sys.path.append('app')
from app.utils import tools

def adjust_nucleosome_positions(dyad_file):
    dyad_file = Path(dyad_file)
    with open(dyad_file, 'r') as file, open(f"{dyad_file}.adjusted", 'w') as out:
        for line in file:
            chrom, start, end, *rest = line.strip().split('\t')
            start = str(int(start) - 1000)
            end = str(int(end) + 1000)
            out.write(f"{chrom}\t{start}\t{end}\t{rest}\n")

    return f"{dyad_file}.adjusted"

def bedtools_intersect_complete_files(mutation_file, dyad_file, output_file, genome_file=None):
    cmd = [
        'bedtools', 'intersect',
        '-a', mutation_file,
        '-b', dyad_file,
        '-wa', '-wb',
        '-sorted'
    ]
    if genome_file:  # If a custom genome file for sorting is provided
        cmd.extend(['-g', genome_file])
    
    with open(output_file, 'w') as out:
        subprocess.run(cmd, stdout=out)

    # Post-processing to create histogram
    post_process_intersection(output_file)

def post_process_intersection(output_file):
    df = pd.read_csv(output_file, sep='\t', header=None)

    # Calculate the difference
    df['Position'] = df[1] - (df[9] + 1000)
    context_grouped = df.groupby(['Position', 6]).size().unstack().fillna(0).astype(int)

    # Reorder columns if necessary
    contexts = tools.contexts_in_iupac('NNN')
    context_grouped = context_grouped.reindex(columns=contexts, fill_value=0)
    
    context_grouped.reset_index(inplace=True)
    context_grouped.to_csv(output_file, sep='\t', index=False)

print(bedtools_intersect_complete_files(  '/home/cam/Documents/repos/ProteoMutics/backend/test/test_data/UV_nucleomutics/UV.mut',
                                    adjust_nucleosome_positions('/home/cam/Documents/repos/ProteoMutics/backend/test/test_data/dyads_nucleomutics/dyads.nuc'),
                                    './backend/test/test_data/UV_new.intersect'))