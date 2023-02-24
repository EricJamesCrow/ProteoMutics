import multiprocessing as mp
import pandas as pd
from pathlib import Path
import traceback
import Tools
from typing import Tuple, List

class DyadFastaCounter:
    def __init__(self, file: Path) -> None:
        self.path = file
        self.context_list = Tools.contexts_in_iupac('NNN')
        self.counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        self.run()

    def run(self) -> None:
        num_blocks = mp.cpu_count()

        with mp.Pool(num_blocks) as pool:
            results = []
            with open(self.path) as f:
                # Get the total number of lines in the file
                f.seek(0, 2) # Move to the end of the file
                end_pos = f.tell() # Get the current position, which is the end of the file
                f.seek(0)  # Reset the file pointer to the beginning of the file

                # Split the file into blocks of approximately equal number of lines
                lines_per_block = end_pos// num_blocks
                block_positions = [0]
                for i in range(1, num_blocks):
                    f.seek(lines_per_block * i)
                    # Read forward to the next newline character
                    f.readline()
                    block_positions.append(f.tell())
                block_positions.append(None)  # Mark the end of the last block

                # Process each block in a separate process
                for i in range(num_blocks):
                    start_pos = block_positions[i]
                    end_pos = block_positions[i+1]
                    result = pool.apply_async(self.process_block, (start_pos, end_pos), error_callback=lambda e: self.handle_error(e, i), callback=self.handle_result)
                    results.append((result, i))

            # Wait for all processes to finish
            for result, i in results:
                result.wait()

            pool.close()

            # Wait for all the processes to finish
            pool.join()

            # Get the results
            self.counts = {k: {sk: v.get(sk, 0) for sk in self.context_list} for d in results for k, v in d[0].get().items()}

        # Write the results to a file
        self.results_to_file()

    def process_block(self, start_pos: int, end_pos: int) -> List[Tuple[int, dict]]:
        counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        lines_counted = 0
        with open(self.path) as f:
            f.seek(start_pos)
            while not end_pos or f.tell() < end_pos:
                line = f.readline()
                lines_counted += 1
                if not line:
                    continue

                sequence = line.split("\t")[1].upper().strip()

                for i in range(-1000,1001):
                    context = sequence[i+1000 : i + 1003]
                    if context not in self.context_list:
                        raise ValueError(f"Error in process {mp.current_process().pid}: Invalid context {context} at position {i}")
                    counts[i][context] += 1

        return [(i, counts[i]) for i in range(-1000,1001)]

    def handle_error(self, error: Exception, task_id: int) -> None:
        print(f"Error in process {task_id}: {error}")

    def handle_result(self, result):
        task_id = mp.current_process().pid
        for pos, counts in result:
            for context in self.context_list:
                self.counts[pos][context] += counts[context]



    def results_to_file(self) -> None:
        output_file = self.path.with_suffix('.txt').with_stem(f'{self.path.stem}_counts')
        df = pd.DataFrame.from_dict(self.counts, orient='index')
        df.columns = self.context_list
        df.index.name = 'Position'
        df.to_csv(output_file, sep='\t')

if __name__ == '__main__':
    mp.freeze_support()
    fasta_counter = DyadFastaCounter(Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_files/dyads_plus-minus_1000_hg19_fasta_filtered.fa'))

# class MutationCounter:
    
#     def __init__(self, intersect_file: Path) -> None:
#         self.path = intersect_file
#         self.counts = [0 for _ in range(1001)]

#     def run(self) -> None:
#         # Count sequences in parallel using a process pool
#         with open(self.path) as f:
#             num_lines = sum(1 for _ in f)

#         num_blocks = mp.cpu_count()
#         block_size = num_lines // num_blocks

#         with open(self.path) as f:
#             header = f.readline().strip().split('\t')
#             # Find the index of any string that contains the substring "chr"
#             chr_positions = [i for i, col in enumerate(header) if 'chr' in col]
#             self.mutation_file_start = chr_positions[0]+1
#             self.dyad_file_start = chr_positions[1]+1

#         # Process each block in parallel
#         with mp.Pool(processes=num_blocks) as pool:
#             results = []
#             with open(self.path) as f:
#                 for i in range(num_blocks):
#                     # Read a block of lines from the file
#                     block = [next(f).strip() for _ in range(block_size)]
#                     # Process the block in a separate process
#                     result = pool.apply_async(self.process_block, (block,))
#                     results.append(result)
#                 remaining_lines = [line.strip() for line in f if line.strip()]
#                 if remaining_lines:
#                     result = pool.apply_async(self.process_block, (remaining_lines,))
#                     results.append(result)

#             pool.close()

#             # Wait for all the processes to finish
#             pool.join()
        
#             # Get the results
#             self.counts = {k: {sk: v.get(sk, 0) for sk in contexts_in_iupac()} for d in dict_list for k, v in d.items()}
            
#             for result in results:
#                 for i, count in enumerate(result.get()):
#                     self.counts[i] += count


#     def process_block(self, block: list[str]) -> list[list[int]]:
#         # creates a list of lists that will hold the nucleotide counts for each position
#         counts = [0 for _ in range(1001)]

#         for line in block:
#             tsv = line.strip().split('\t')
#             counts[int(tsv[counts])-int(tsv[counts])] += 1

#         return counts

# def g_only_normalize_counts():
#     with open('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500_counts.txt', 'r') as f:
#         header = f.readline()
#         g_list = [float(line.strip().split("\t")[3]) for line in f]
#     return g_list
