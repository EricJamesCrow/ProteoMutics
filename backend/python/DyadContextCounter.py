import multiprocessing as mp  # import multiprocessing module to handle parallel computation
import pandas as pd  # import pandas for handling data in DataFrame format
from pathlib import Path  # import Path from pathlib for handling paths
import Tools  # import Tools module from the current package
import traceback  # import traceback for printing stack trace of an exception
from typing import Tuple, List  # import Tuple and List from typing for annotating function signatures


class DyadFastaCounter:
    def __init__(self, file: Path, output_dir: Path) -> None:
        """Initializes the DyadFastaCounter object and runs the counting process.

        Args:
            file (Path): A path to the file to be processed.
            output_dir (Path): A path to the output directory where the results will be saved.
        """
        # storing the input parameters and initializing required variables
        self.path = file
        self.output_dir = output_dir
        self.context_list = Tools.contexts_in_iupac('NNN')  # create a list of trinucleotide contexts
        self.counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}  # initialize the counts for all contexts
        self.results = []  # create a list to store the results
        self.run()  # run the counting process

    def handle_error(self, error: Exception, task_id: int) -> None:
        """Handles the error occurred in a subprocess and prints it out with a traceback.

        Args:
            error (Exception): The occurred error.
            task_id (int): The ID of the failed task.
        """
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)  # print the traceback of the error

    def results_to_file(self, context_list: list, counts: dict, path: Path, output_dir) -> None:
        """Writes the results to a file.

        Args:
            context_list (list): A list of context.
            counts (dict): A dictionary of counts.
            path (Path): A path to the file being processed.
            output_dir (Path): A path to the output directory.
        """
        output_file = output_dir / path.with_name(f'{path.stem}.counts').name  # define the output file path
        df = pd.DataFrame.from_dict(counts, orient='index')  # create a DataFrame from the counts dictionary
        df.columns = context_list  # set column names
        df.index.name = 'Position'  # set index name
        df.to_csv(output_file, sep='\t')  # write the DataFrame to a file

    def process_block(self, start_pos: int, end_pos: int, context_list: list, path: Path) -> List[Tuple[int, dict]]:
        """Processes a block of the file from the given start and end positions.

        Args:
            start_pos (int): The start position of the block.
            end_pos (int): The end position of the block.
            context_list (list): A list of context.
            path (Path): A path to the file being processed.

        Raises:
            ValueError: If an invalid context is found.

        Returns:
            List[Tuple[int, dict]]: A list of tuples where each tuple contains a process ID and a resulting dictionary.
        """
        counts = {i: {key: 0 for key in context_list} for i in range(-1000,1001)}  # initialize the counts for all contexts
        with open(path) as f:
            f.seek(start_pos)  # move to the start position
            while not end_pos or f.tell() < end_pos:  # process the block until the end position is reached
                line = f.readline()  # read a line from the file
                if not line:  # if the line is empty (the end of the file is reached)
                    break  # break the loop

                sequence = line.split("\t")[1].upper().strip()  # extract the sequence from the line

                for i in range(-1000,1001):  # iterate through each position in the sequence
                    context = sequence[i+1000 : i + 1003]  # get the context at the current position
                    if context not in context_list:  # if the context is not valid
                        raise ValueError(f"Error in process {mp.current_process().pid}: Invalid context {context} at position {i}")  # raise an error
                    counts[i][context] += 1  # increment the count for the context at the current position
        
        return counts  # return the counts dictionary

    def run(self) -> None:
        """Runs the counting process using multiprocessing."""
        num_blocks = mp.cpu_count()  # get the number of CPU cores
        with mp.Pool(num_blocks) as pool:  # create a pool of processes
            with open(self.path) as f:
                f.seek(0, 2)  # move to the end of the file
                end_pos = f.tell()  # get the end position of the file
                f.seek(0)  # move back to the beginning of the file

                bytes_per_block = end_pos // num_blocks  # calculate the approximate number of bytes per block
                block_positions = [0]  # initialize the block positions list with the first block starting at the beginning of the file
                for i in range(1, num_blocks):
                    f.seek(bytes_per_block * i)  # move to the start position of the next block
                    f.readline()  # read until the end of the current line (to not break the line)
                    block_positions.append(f.tell())  # add the end position of the current block to the block positions list
                block_positions.append(None)  # add the end of the last block

                results = []  # create a list to store the results
                for i in range(num_blocks):  # iterate through each block
                    start_pos = block_positions[i]  # get the start position of the current block
                    end_pos = block_positions[i+1]  # get the end position of the current block
                    result = pool.apply_async(self.process_block, (start_pos, end_pos, self.context_list, self.path), error_callback=lambda e: self.handle_error(e, i))  # process the block in a separate process
                    results.append((result, i))  # add the result to the results list

            for result, i in results:  # iterate through each result
                result.wait()  # wait until the result is ready

            pool.close()  # close the pool
            pool.join()  # wait for all processes to finish

            for result, i in results:  # iterate through each result
                self.results.append(result.get())  # get the result and add it to the results list

            for result in self.results:  # iterate through each result
                for i in range(-1000, 1001):  # iterate through each position
                    for context in self.context_list:  # iterate through each context
                        self.counts[i][context] += result[i][context]  # increment the count for the context at the current position

        self.results_to_file(self.context_list, self.counts, self.path, self.output_dir)  # write the results to a file
