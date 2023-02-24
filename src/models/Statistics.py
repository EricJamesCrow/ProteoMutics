import multiprocessing as mp
import pandas as pd
from pathlib import Path
import Tools
from typing import Tuple, List

class DyadFastaCounter:
    def __init__(self, file: Path) -> None:
        """Creates and runs a class that counts trinucleotide contexts at every position relative to a pool of dyads.

        Args:
            file (Path): ex: pathlib.Path('path/to/file.txt') format file input. Path object path to dyad file
        """
        self.path = file
        self.context_list = Tools.contexts_in_iupac('NNN')
        self.counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        self.lock = mp.Lock()  # create a lock object
        self.run()
    
    def handle_result(self, result):
        """Combines results from `process_block()` functions and adds them to the DyadFastaCounter `counts` property.
        """
        for pos, counts in result:
            with self.lock:  # acquire the lock before accessing self.counts
                for context in self.context_list:
                    self.counts[pos][context] += counts[context]

    def handle_error(self, error: Exception, task_id: int) -> None:
        """Prints the error from the process to the terminal
        """
        print(f"Error in process {task_id}: {error}")

    def results_to_file(self, context_list: list, counts: dict, path: Path) -> None:
        output_file = path.with_name(f'{path.stem}_counts.txt')
        df = pd.DataFrame.from_dict(counts, orient='index')
        df.columns = context_list
        df.index.name = 'Position'
        df.to_csv(output_file, sep='\t')
    
    def process_block(self, start_pos: int, end_pos: int, context_list: list, path: Path) -> List[Tuple[int, dict]]:
        """Processes a block from the file from the given start and end positions. It will create a dictionary with positions
        relative to the dyad and count all the diffent trinucleotide contexts at the given position.

        Args:
            start_pos (int): byte file pointer to the start positon
            end_pos (int): byte file pointer to the end positon
            context_list (list): the list of all 96 possible trinucleotide contexts to count
            path (Path): ex: pathlib.Path('path/to/file.txt') format file input. Path object path to dyad file

        Raises:
            ValueError: Error if the context cannot be added to the dictionary.

        Returns:
            List[Tuple[int, dict]]: [process_id, resulting nested dictionary]
        """
        counts = {i: {key: 0 for key in context_list} for i in range(-1000,1001)}
        lines_counted = 0
        with open(path) as f:
            f.seek(start_pos)
            while not end_pos or f.tell() < end_pos:
                line = f.readline()
                lines_counted += 1
                if not line:
                    continue

                sequence = line.split("\t")[1].upper().strip()

                for i in range(-1000,1001):
                    context = sequence[i+1000 : i + 1003]
                    if context not in context_list:
                        raise ValueError(f"Error in process {mp.current_process().pid}: Invalid context {context} at position {i}")
                    counts[i][context] += 1

        return [(i, counts[i]) for i in range(-1000,1001)]

    def run(self) -> None:
        """Runs the program by..
        """
        num_blocks = mp.cpu_count()

        with mp.Pool(num_blocks) as pool:
            results = []
            with open(self.path) as f:
                # Get the total number of lines in the file
                f.seek(0, 2) # Move to the end of the file
                end_pos = f.tell() # Get the current position, which is the end of the file
                f.seek(0)  # Reset the file pointer to the beginning of the file

                # Split the file into blocks of approximately equal number of lines
                bytes_per_block = end_pos // num_blocks
                block_positions = [0]
                for i in range(1, num_blocks):
                    f.seek(bytes_per_block * i)
                    # Read forward to the next newline character
                    f.readline()
                    block_positions.append(f.tell())
                block_positions.append(None)  # Mark the end of the last block

                # Process each block in a separate process
                for i in range(num_blocks):
                    start_pos = block_positions[i]
                    end_pos = block_positions[i+1]
                    result = pool.apply_async(self.process_block, (start_pos, end_pos, self.context_list, self.path), error_callback=lambda e: self.handle_error(e, i), callback=self.handle_result)
                    results.append((result, i))

            # Wait for all processes to finish
            for result, i in results:
                result.wait()

            pool.close()

            # Wait for all the processes to finish
            pool.join()

            # # Get the results
            # counts = {k: {sk: v.get(sk, 0) for sk in self.context_list} for d in results for k, v in d[0].get().items()}

        # Write the results to a file
        self.results_to_file(self.context_list, self.counts, self.path)

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
