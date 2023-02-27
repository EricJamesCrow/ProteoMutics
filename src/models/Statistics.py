import multiprocessing as mp
import pandas as pd
from pathlib import Path
import Tools
import traceback
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
        self.results = []
        self.run()

    def handle_error(self, error: Exception, task_id: int) -> None:
        """Prints the error from the process to the terminal, including a traceback."""
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def results_to_file(self, context_list: list, counts: dict, path: Path) -> None:
        output_file = path.with_name(f'{path.stem}_counts.txt')
        df = pd.DataFrame.from_dict(counts, orient='index')
        df.columns = context_list
        df.index.name = 'Position'
        df.to_csv(output_file, sep='\t')
    
    def process_block(self, start_pos: int, end_pos: int, context_list: list, path: Path) -> List[Tuple[int, dict]]:
        """Processes a block from the file from the given start and end positions. It will create a dictionary with positions relative to the dyad and count all the diffent trinucleotide contexts at the given position.

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
        with open(path) as f:
            f.seek(start_pos)
            while not end_pos or f.tell() < end_pos:
                line = f.readline()
                if not line:
                    break

                sequence = line.split("\t")[1].upper().strip()

                for i in range(-1000,1001):
                    context = sequence[i+1000 : i + 1003]
                    if context not in context_list:
                        raise ValueError(f"Error in process {mp.current_process().pid}: Invalid context {context} at position {i}")
                    counts[i][context] += 1
        
        return counts

    def run(self) -> None:
        """Runs the program by..
        """
        num_blocks = mp.cpu_count()
        with mp.Pool(num_blocks) as pool:
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
                results = []
                for i in range(num_blocks):
                    start_pos = block_positions[i]
                    end_pos = block_positions[i+1]
                    result = pool.apply_async(self.process_block, (start_pos, end_pos, self.context_list, self.path), error_callback=lambda e: self.handle_error(e, i))
                    results.append((result, i))

            # Wait for all processes to finish
            for result, i in results:
                result.wait()

            # Close the pool so no more processes can be added to it
            pool.close()

            # Wait for all the processes to finish
            pool.join()

            for result, i in results:
                self.results.append(result.get())

            for result in self.results:
                for i in range(-1000, 1001):
                    for context in self.context_list:
                        self.counts[i][context] += result[i][context]

        # Write the results to a file
        self.results_to_file(self.context_list, self.counts, self.path)

class MutationIntersector:
    
    def __init__(self, mutation_file: Path, dyad_file: Path) -> None:
        self.mutation_file = mutation_file
        self.dyad_file = dyad_file
        self.context_list = Tools.contexts_in_iupac('NNN')
        self.counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        self.results = []
        self.run()

    def handle_error(self, error: Exception, task_id: int) -> None:
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def process_block(dyad_start: int, dyad_end: int, mut_start: int, mut_end: int, context_list: list[str], mutation_file: Path, dyad_file: Path) -> List[Tuple[int, dict]]:
        counts = {i: {key: 0 for key in context_list} for i in range(-1000,1001)}
        with open(dyad_file) as d_file, open(mutation_file) as m_file:
            m_file.seek(mut_start)
            d_file.seek(dyad_start)
            mut_line = m_file.readline()
            dyad_line = d_file.readline()
            while not (dyad_end and mut_end) or (m_file.tell() <= mut_end and d_file.tell() <= dyad_end) or mut_line or dyad_line:
                # initialize mut_data variables and reads in the next line
                mut_data = mut_line.strip().split('\t')
                mut_chrom, mut_0, mut_1 = mut_data[:3]
                mut_0, mut_1 = int(mut_0), int(mut_1)
                # initialize dyad_data variables and reads in the next line
                dyad_data = mut_line.strip().split('\t')
                dyad_chrom, dyad_0, dyad_1 = dyad_data[:3]
                dyad_0, dyad_1 = int(dyad_0), int(dyad_1)
                if mut_chrom != dyad_chrom:
                    print('ERROR!')
                    break
                if mut_0 > dyad_0 and mut_1 < dyad_1:


                for i in range(-1000,1001):
                    context = sequence[i+1000 : i + 1003]
                    if context not in context_list:
                        raise ValueError(f"Error in process {mp.current_process().pid}: Invalid context {context} at position {i}")
                    counts[i][context] += 1
        
        return counts

    def run(self) -> None:
        with mp.Pool(mp.cpu_count()) as pool:
            with open(self.dyad_file, 'r') as dyad_file, open(self.mutation_file, 'r') as mut_file:
                dyad_chroms = [0]
                dyad_line = dyad_file.readline()
                while dyad_line:
                    current_chrom = dyad_line.strip().split('\t')[0]
                    location = dyad_file.tell()
                    next_chrom = dyad_file.readline().strip().split('\t')[0]
                    if current_chrom != next_chrom:
                        dyad_chroms.append(location)
                    dyad_line = dyad_file.readline()
                dyad_chroms.append(None)
                
                mut_chroms = [0]
                mut_line = mut_file.readline()
                while mut_line:
                    current_chrom = mut_line.strip().split('\t')[0]
                    location = mut_file.tell()
                    next_chrom = mut_file.readline().strip().split('\t')[0]
                    if current_chrom != next_chrom:
                        mut_chroms.append(location)
                    mut_line = dyad_file.readline()
                mut_chroms.append(None)

                results = []
                for i in range(len(dyad_chroms)):
                    dyad_start = dyad_chroms[i]
                    dyad_end = dyad_chroms[i+1]
                    mut_start = mut_chroms[i]
                    mut_end = mut_chroms[i+1]
                    result = pool.apply_async(self.process_block, (dyad_start, dyad_end, mut_start, mut_end, self.context_list, self.mutation_file, self.dyad_file), error_callback=lambda e: self.handle_error(e, i))
                    results.append((result, i))