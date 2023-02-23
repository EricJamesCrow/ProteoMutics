import multiprocessing as mp
from pathlib import Path

class DyadFastaCounter:

    def __init__(self, file: Path) -> None:
        self.path = file
        self.counts = [[0] * 4 for _ in range(1001)]

    def run(self) -> None:
        # Count sequences in parallel using a process pool
        with open(self.path) as f:
            num_lines = sum(1 for _ in f)

        num_blocks = mp.cpu_count()
        block_size = num_lines // num_blocks

        # Process each block in parallel
        with mp.Pool(processes=num_blocks) as pool:
            results = []
            with open(self.path) as f:
                for i in range(num_blocks):
                    # Read a block of lines from the file
                    block = [next(f).strip().split('\t')[1].upper() for _ in range(block_size)]
                    # Process the block in a separate process
                    result = pool.apply_async(self.process_block, (block,))
                    results.append(result)
                remaining_lines = [line.strip().split('\t')[1].upper() for line in f if line.strip()]
                if remaining_lines:
                    result = pool.apply_async(self.process_block, (remaining_lines,))
                    results.append(result)

            pool.close()

            # Wait for all the processes to finish
            pool.join()

            # Get the results
            for result in results:
                for i, counts in enumerate(result.get()):
                    for j, count in enumerate(counts):
                        self.counts[i][j] += count

        # Write the results to a file
        self.results_to_file()


    def process_block(self, block: list[str]) -> list[list[int]]:
        # creates a list of lists that will hold the nucleotide counts for each position
        counts = [[0] * 4 for _ in range(1001)]

        # counts the nucleotides at each position
        for sequence in block:
            for i, base in enumerate(sequence):
                if base == 'A':
                    counts[i][0] += 1
                elif base == 'C':
                    counts[i][1] += 1
                elif base == 'G':
                    counts[i][2] += 1
                elif base == 'T':
                    counts[i][3] += 1

        return counts

    def results_to_file(self) -> None:
        output_file = self.path.with_name(f'{self.path.stem}_counts.txt')
        with open(output_file, 'w') as o:
            o.write('Position\tA\tC\tG\tT\n')
            for i in range(1001):
                # Get the counts for this position from self.counts
                counts = self.counts[i]

                # Compute the total count for this position
                total_count = sum(counts)

                # Compute the percentages for each base at this position
                percentages = [count / total_count for count in counts]

                # Write the percentages to the file
                o.write(f'{i-500}\t{percentages[0]:.4f}\t{percentages[1]:.4f}\t{percentages[2]:.4f}\t{percentages[3]:.4f}\n')

class MutationCounter:
    
    def __init__(self, intersect_file: Path) -> None:
        self.path = intersect_file
        self.counts = [0 for _ in range(1001)]

    def run(self) -> None:
        # Count sequences in parallel using a process pool
        with open(self.path) as f:
            num_lines = sum(1 for _ in f)

        num_blocks = mp.cpu_count()
        block_size = num_lines // num_blocks

        with open(self.path) as f:
            header = f.readline().strip().split('\t')
            # Find the index of any string that contains the substring "chr"
            chr_positions = [i for i, col in enumerate(header) if 'chr' in col]
            self.mutation_file_start = chr_positions[0]+1
            self.dyad_file_start = chr_positions[1]+1

        # Process each block in parallel
        with mp.Pool(processes=num_blocks) as pool:
            results = []
            with open(self.path) as f:
                for i in range(num_blocks):
                    # Read a block of lines from the file
                    block = [next(f).strip() for _ in range(block_size)]
                    # Process the block in a separate process
                    result = pool.apply_async(self.process_block, (block,))
                    results.append(result)
                remaining_lines = [line.strip() for line in f if line.strip()]
                if remaining_lines:
                    result = pool.apply_async(self.process_block, (remaining_lines,))
                    results.append(result)

            pool.close()

            # Wait for all the processes to finish
            pool.join()
        
            # Get the results
            for result in results:
                for i, count in enumerate(result.get()):
                    self.counts[i] += count


    def process_block(self, block: list[str]) -> list[list[int]]:
        # creates a list of lists that will hold the nucleotide counts for each position
        counts = [0 for _ in range(1001)]

        for line in block:
            tsv = line.strip().split('\t')
            counts[int(tsv[counts])-int(tsv[counts])] += 1

        return counts

def g_only_normalize_counts():
    with open('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500_counts.txt', 'r') as f:
        header = f.readline()
        g_list = [float(line.strip().split("\t")[3]) for line in f]
    return g_list
