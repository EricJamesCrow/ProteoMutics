from pathlib import Path
import pandas as pd
import multiprocessing as mp

def position_percentages_in_dyad(dyad_fasta_file: Path):
    """creates a file using the expanded dyad position file to calculate the percentages of each base at each position to use later in normalization.

    Args:
        dyad_fasta_file (Path): .fa file coming from BedtoolsCommands.bedtools_getfasta() 
    """
    
    # creates a dictionary that will keep track of each nucleotide at each position
    counts = {}
    for i in range(-500,501):
        counts.setdefault(i, [0,0,0,0,0])

    # opens the dyad file and reads through the information
    with open(dyad_fasta_file, 'r') as f:
        for line in f:
            fasta_info = line
            sequence = f.readline()
            for i, base in zip(range(-500,501), sequence):
                if base == 'A': counts[i][0] += 1
                elif base == 'C': counts[i][1] += 1
                elif base == 'G': counts[i][2] += 1
                elif base == 'T': counts[i][3] += 1
                else: counts[i][4] += 1
    
    # generates percentages at each position 
    percentages = {}
    for i in range(-500,501):
        total = sum(counts[i])
        percentages[i] = []
        for counts in counts[i]:
            percentages[i].append(counts/total)
    
    # writes the dictionary to a file using pandas for format
    df = pd.DataFrame.from_dict(percentages, orient='index', columns=['A','C','G','T','N'])
    df.to_csv(dyad_fasta_file.with_name(f'{dyad_fasta_file.stem}_counts.txt'), sep = '\t')



########################### multiprocess for counting #######################################33
# def mp_position_percentages_in_dyad(fasta_file: Path):
#     '''
    
#     '''
    
#     with open(fasta_file, 'r') as f:
#         process_id = -1
#         line = f.readline()
#         while line:
#             if '_' in line: line = f.readline()
#             if 'M' in line: line = f.readline()
#             if '>' in line[0]:
#                 process_id += 1
#                 chromosome_number = line.strip().split('>')[1]
#                 fasta_position = f.tell()
#                 pool.apply_async(func = count_chromosome, args=[process_id, fasta_file, fasta_position, context_length, chromosome_number], callback = collect_result)
#             line = f.readline()

# def count_chromosome(process_id: int, file: str, position:int, context_length: int, chromosome_number: str):
#     """Counts `context_length` sequences starting at the given file `position` in a file until the end of the `chromosome`.
#         Returns the counts of the chromosome in a dictionary with the contexts as `keys` and the counts as `values`."""
#     with open(file, 'r') as f:
#         context_dict = {}
#         f.seek(position)
#         chromosome = f.readline().strip().upper()
#         next_line = chromosome
#         in_chromosome = True
#         while next_line and in_chromosome:
#             while len(chromosome) >= context_length:
#                 context_dict[chromosome[:context_length]] = context_dict.setdefault(chromosome[:context_length], 0) + 1
#                 chromosome = chromosome[1:]
#             else:
#                 next_line = f.readline().strip().upper()
#                 if '>' in next_line:
#                     in_chromosome = False
#                     break
#                 else:
#                     chromosome += next_line
#                     continue
#         return (process_id, context_dict)


# # Step 2: Define callback function to collect the output in `results`
# def collect_result(result):
#     global results
#     results.append(result)

# # Merge dictionaroes together to combine resuls after collection
# def merge_dicts(keep: dict, add: dict):
#     for k, v in add.items():
#         try: keep[k] += v
#         except KeyError: keep[k] = v
#     return keep

# # Step 3: Use loop to parallelize


# def results_to_file(output_file: str):
#     with open(output_file, 'w') as o:
#         o.write('CONTEXTS\tCOUNTS\n')
#         global genome_counts
#         for k, v in genome_counts.items():
#             o.write(f'{k}\t{v}\n')

# pool = mp.Pool(mp.cpu_count())
# fasta_file = 'hg19.fa'
# context_length = 3
# count_fasta_contexts(fasta_file, context_length)
# # Step 4: Close Pool and let all the processes complete    
# pool.close()
# pool.join()  # postpones the execution of next line of code until all processes in the queue are done.

# for r in results: merge_dicts(genome_counts, r[1])
# results_to_file('hg19_3mer_contexts.txt')
# print(f'Process Complete!\nFinished counting {context_length}mer contexts in {fasta_file}.\nProcess completed in {(time.time()-start_time):.2f} seconds.\nProcess complete at {datetime.datetime.now()}')