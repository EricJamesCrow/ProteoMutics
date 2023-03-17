import multiprocessing as mp

results = []
genome_counts = {}
program_running = True

# count each chromosome's context values
def count_chromosome(i: int, file: str, position:int, context_length: int, chromosome_number: str):
    """Counts `context_length` sequences starting at the given file `position` in a file until the end of the `chromosome`.
        Returns the counts of the chromosome in a dictionary with the contexts as `keys` and the counts as `values`."""
    with open(file, 'r') as f:
        context_dict = {}
        f.seek(position)
        chromosome = f.readline().strip().upper()
        next_line = chromosome
        in_chromosome = True
        while next_line and in_chromosome:
            while len(chromosome) >= context_length:
                context_dict[chromosome[:context_length]] = context_dict.setdefault(chromosome[:context_length], 0) + 1
                chromosome = chromosome[1:]
            else:
                next_line = f.readline().strip().upper()
                if '>' in next_line:
                    in_chromosome = False
                    break
                else:
                    chromosome += next_line
                    continue
        return (i, context_dict)

# Step 2: Define callback function to collect the output in `results`
def collect_result(result):
    global results
    results.append(result)

# Merge dictionaroes together to combine resuls after collection
def merge_dicts(keep: dict, add: dict):
    for k, v in add.items():
        try: keep[k] += v
        except KeyError: keep[k] = v
    return keep

# Step 3: Use loop to parallelize
def count_fasta_contexts(fasta_file: str, context_length: int):
    """Counts all contexts within a `fasta_file` of given `context_length`

    Args:
        `fasta_file` (str): given file path for the fasta file as a string\n
        `context_length` (int): the length of the context you want to count, ex: 3
    """    
    with open(fasta_file, 'r') as f:
        i = -1
        line = f.readline()
        while line:
            if '_' in line: line = f.readline()
            if 'M' in line: line = f.readline()
            if '>' in line[0]:
                i += 1
                chromosome_number = line.strip().split('>')[1]
                fasta_position = f.tell()
                pool.apply_async(func = count_chromosome, args=[i, fasta_file, fasta_position, context_length, chromosome_number], callback = collect_result)
            line = f.readline()

def results_to_file(output_file: str):
    with open(output_file, 'w') as o:
        o.write('CONTEXTS\tCOUNTS\n')
        global genome_counts
        for k, v in genome_counts.items():
            o.write(f'{k}\t{v}\n')

pool = mp.Pool(mp.cpu_count())
fasta_file = '/media/cam/Data9/CortezAnalysis/pipeline_files/hg19.fa'
context_length = 4
count_fasta_contexts(fasta_file, context_length)
# Step 4: Close Pool and let all the processes complete    
pool.close()
pool.join()  # postpones the execution of next line of code until all processes in the queue are done.

for r in results: merge_dicts(genome_counts, r[1])
results_to_file('hg19_4mer_contexts.txt')