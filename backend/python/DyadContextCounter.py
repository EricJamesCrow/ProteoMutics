import multiprocessing as mp
import pandas as pd
from pathlib import Path
import Tools
import traceback
from typing import Tuple, List


class DyadFastaCounter:
    def __init__(self, file: Path, output_dir: Path) -> None:
        """Creates and runs a class that counts trinucleotide contexts at every position relative to a pool of dyads.

        Args:
            file (Path): ex: pathlib.Path('path/to/file.txt') format file input. Path object path to dyad file
        """
        self.path = file
        self.output_dir = output_dir
        self.context_list = Tools.contexts_in_iupac('NNN')
        self.counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        self.results = []
        self.run()

    def handle_error(self, error: Exception, task_id: int) -> None:
        """Prints the error from the process to the terminal, including a traceback."""
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def results_to_file(self, context_list: list, counts: dict, path: Path, output_dir) -> None:
        output_file = output_dir / path.with_name(f'{path.stem}.counts').name
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
        self.results_to_file(self.context_list, self.counts, self.path, self.output_dir)