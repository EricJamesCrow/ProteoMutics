import multiprocessing as mp
import pandas as pd
from pathlib import Path
import Tools
import traceback
from typing import Tuple, List
import time

def df_division_and_standardization(mutation_counts: Path, dyad_counts: Path, iupac: str):
    mutations_df = pd.read_csv(mutation_counts, sep= '\t', index_col=0, header=0)
    dyads_df = pd.read_csv(dyad_counts, sep= '\t', index_col=0, header=0)
    contexts = Tools.contexts_in_iupac('NCN')
    all_contexts = contexts
    for item in contexts:
        rev_comp = Tools.reverse_complement(item)
        if rev_comp not in all_contexts:
            all_contexts.append(rev_comp)
    new_mut_df = mutations_df.loc[:,all_contexts]
    new_dyad_df = dyads_df.loc[:,all_contexts]
    results_dict = {}
    i = -1000
    for mut_index, mut_row in new_mut_df.iterrows():
        results_dict[i] = [(sum(mut_row.tolist())/sum(new_dyad_df.loc[mut_index].tolist()))]
        i += 1
    result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])
    result_df_normalized = result_df.divide(result_df.median())
    return result_df_normalized

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
        self.dyad_chrom_names = []
        self.mutations_chrom_names = []
        self.run()

    def handle_error(self, error: Exception, task_id: int) -> None:
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def results_to_file(self, context_list: list, counts: dict, mutation_file: Path, dyad_file: Path) -> None:
        output_file = mutation_file.with_name(f'{mutation_file.stem}_{dyad_file.stem}_intersected_mutations_counts.txt')
        df = pd.DataFrame.from_dict(counts, orient='index')
        df.columns = context_list
        df.index.name = 'Position'
        df.to_csv(output_file, sep='\t')

    def process_block(self, dyad_start_position: int, dyad_end_position: int, mut_start_position: int, mut_end_position: int, context_list: list[str], mutation_file_path: Path, dyad_file_path: Path, process_id: int) -> List[Tuple[int, dict]]:
        counts = {i: {key: 0 for key in context_list} for i in range(-1000,1001)}
        with open(dyad_file_path) as dyad_file, open(mutation_file_path) as mut_file:
            dyad_file.seek(dyad_start_position)
            mut_file.seek(mut_start_position)
            jump_back_position = mut_start_position
            mut_data = mut_file.readline().strip().split('\t')
            mut_start = int(mut_data[1])
            context = mut_data[6]
            while True:
                dyad_data = dyad_file.readline().strip().split('\t')                
                if dyad_file.tell() > dyad_end_position:
                    break
                if dyad_data == ['']:
                    break
                dyad_start = int(dyad_data[1])
                while mut_start-dyad_start < -1000:
                    jump_back_position = mut_file.tell()
                    mut_data = mut_file.readline().strip().split('\t')
                    if mut_file.tell() > mut_end_position:
                        break
                    if mut_data == ['']:
                        break
                    mut_start = int(mut_data[1])
                    context = mut_data[6]
                while -1000 <= mut_start-dyad_start <= 1000:
                    counts[mut_start-dyad_start][context] += 1
                    mut_data = mut_file.readline().strip().split('\t')
                    if mut_file.tell() > mut_end_position:
                        break
                    if mut_data == ['']:
                        break
                    mut_start = int(mut_data[1])
                    context = mut_data[6]
                mut_file.seek(jump_back_position)
                mut_data = mut_file.readline().strip().split('\t')
                if mut_file.tell() > mut_end_position:
                    break
                if mut_data == ['']:
                    break
                mut_start = int(mut_data[1])
                context = mut_data[6]
                
        return counts

    def run(self) -> None:
        with mp.Pool(mp.cpu_count()) as pool:
            with open(self.dyad_file, 'r') as dyad_file, open(self.mutation_file, 'r') as mut_file:
                start_time = time.time()
                overall_time = start_time
                #### make process run with MB blocks to read file faster ####                
                dyad_chroms = [0]
                current_chrom = dyad_file.readline().strip().split('\t')[0]
                while current_chrom != '':
                    location = dyad_file.tell()
                    next_chrom = dyad_file.readline().strip().split('\t')[0]
                    if current_chrom != next_chrom or next_chrom == '':
                        dyad_chroms.append(location)
                        self.dyad_chrom_names.append(current_chrom)
                    current_chrom = next_chrom
                dyad_file.seek(0,2)
                dyad_chroms[-1] = dyad_file.tell()
                self.dyad_chrom_names.append(current_chrom)
                print('Pre-processed dyad file.', (time.time()-start_time)/60, 'minutes')
                start_time = time.time()
                mut_chroms = [0]
                current_chrom = mut_file.readline().strip().split('\t')[0]
                while current_chrom != '':
                    location = mut_file.tell()
                    next_chrom = mut_file.readline().strip().split('\t')[0]
                    if current_chrom != next_chrom or next_chrom == '':
                        mut_chroms.append(location)
                        self.mutations_chrom_names.append(current_chrom)
                    current_chrom = next_chrom
                mut_file.seek(0,2)
                mut_chroms[-1] = mut_file.tell()
                self.mutations_chrom_names.append(current_chrom)
                process_time = time.time()
                print('Pre-processed mutation file.', (time.time()-start_time)/60, 'minutes')
                start_time = time.time()
                results = []
                if self.mutations_chrom_names != self.dyad_chrom_names:
                    print('NOT THE SAME')
                for i in range(len(mut_chroms)-1):
                    dyad_start = dyad_chroms[i]
                    dyad_end = dyad_chroms[i+1]
                    mut_start = mut_chroms[i]
                    mut_end = mut_chroms[i+1]
                    result = pool.apply_async(self.process_block, (dyad_start, dyad_end, mut_start, mut_end, self.context_list, self.mutation_file, self.dyad_file, i), error_callback=lambda e: self.handle_error(e, i))
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
        self.results_to_file(self.context_list, self.counts, self.mutation_file, self.dyad_file)
        print('Counting time:', (time.time() - process_time)/60, 'minutes')
        print('Overall time:', (time.time() - overall_time)/60, 'minutes')

# counts all the different positions in the dyad file
import multiprocessing as mp
import Statistics
from pathlib import Path

if __name__ == '__main__':
    mp.freeze_support()
    fasta_counter = Statistics.MutationIntersector(
        mutation_file = Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_69-70_adjusted_filtered_sorted.bed'),
        # mutation_file = Path('/media/cam/Data9/CortezAnalysis/Cam_calls/Analysis/vcf_files/concat/KM_treated_filtered_sorted.bed'),
        dyad_file = Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_filtered_sorted.bed')
    )
