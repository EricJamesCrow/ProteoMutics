from app.utils import tools

import multiprocessing as mp
import pandas as pd
from pathlib import Path
import traceback


class MutationIntersector:
    
    def __init__(self, mutation_file: Path | str, dyad_file: Path | str, mut_context='NNN', mutation_type='N>N') -> None:
        self.mutation_file = Path(mutation_file)
        self.dyad_file = Path(dyad_file)
        self.output_file = mutation_file.with_name(f'{mutation_file.stem}_{dyad_file.stem}.intersect')
        self.mut_context = tools.contexts_in_iupac(mut_context)
        self.mutation_type = tools.mutation_combinations(mutation_type)
        self.context_list = tools.contexts_in_iupac('NNN')
        self.counts = self.initialize_counts()
        self.results = []
        self.dyad_chrom_names = []
        self.mutations_chrom_names = []

    def initialize_counts(self) -> dict:
        return {i: {key: 0 for key in self.context_list} for i in range(-1000, 1001)}

    @staticmethod
    def handle_error(error: Exception, task_id: int) -> None:
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def results_to_file(self) -> None:
        df = pd.DataFrame.from_dict(self.counts, orient='index')
        df.columns = self.context_list
        df.index.name = 'Position'
        df.to_csv(self.output_file, sep='\t')

    def process_block(self, dyad_start_position: int, dyad_end_position: int, mut_start_position: int, mut_end_position: int) -> dict:
        # Initializing a dictionary similar to the one in __init__ to store counts.
        counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        with open(self.dyad_file) as dyad_file, open(self.mutation_file) as mut_file:  # Opening both dyad and mutation files.
            dyad_file.seek(dyad_start_position)  # Moving dyad_file's read/write pointer to dyad_start_position.
            mut_file.seek(mut_start_position)  # Moving mut_file's read/write pointer to mut_start_position.
            jump_back_position = mut_start_position  # Storing mut_start_position in jump_back_position.
            mut_data = mut_file.readline().strip().split('\t')  # Reading a line from mut_file, stripping whitespaces, splitting it by tabs, and storing in mut_data.
            while mut_data[6] not in self.mut_context and mut_data[7] not in self.mutation_type:
                mut_data = mut_file.readline().strip().split('\t')
            mut_start = int(mut_data[1])  # Converting second item of mut_data to integer and storing in mut_start.
            context = mut_data[6]  # Storing sixth item of mut_data in context.
            while True:
                # The dyad_data line reads from a file, removes leading and trailing spaces, and separates by tab.
                dyad_data = dyad_file.readline().strip().split('\t')                
                if dyad_file.tell() > dyad_end_position:
                    break
                if dyad_data == ['']:
                    break
                dyad_start = int(dyad_data[1])

                # This loop checks the distance between the start positions of mutations and dyads. If it's less than -1000, it moves forward in the mutations file.
                while mut_start-dyad_start < -1000:
                    jump_back_position = mut_file.tell()
                    mut_data = mut_file.readline().strip().split('\t')
                    if mut_file.tell() > mut_end_position:
                        break
                    if mut_data == ['']:
                        break
                    mut_start = int(mut_data[1])
                    context = mut_data[6]

                # This loop checks if the mutation start position is within a 1000 base pairs range from the dyad start position. If it is, it increments the count for the context of that mutation.
                while -1000 <= mut_start-dyad_start <= 1000:
                    counts[mut_start-dyad_start][context] += 1
                    mut_data = mut_file.readline().strip().split('\t')
                    if mut_file.tell() > mut_end_position:
                        break
                    if mut_data == ['']:
                        break
                    mut_start = int(mut_data[1])
                    context = mut_data[6]

                # Here, it sets the pointer of the mutation file back to the start of the previous dyad.
                mut_file.seek(jump_back_position)
                mut_data = mut_file.readline().strip().split('\t')
                if mut_file.tell() > mut_end_position:
                    break
                if mut_data == ['']:
                    break
                mut_start = int(mut_data[1])
                context = mut_data[6]
                
        return counts

    def extract_chrom_names(self, file_path: Path):
        chroms = [0]
        chrom_names = []
        with open(file_path, 'r') as file:
            current_chrom = file.readline().strip().split('\t')[0]
            while current_chrom:
                location = file.tell()
                next_chrom = file.readline().strip().split('\t')[0]
                if current_chrom != next_chrom or not next_chrom:
                    chroms.append(location)
                    chrom_names.append(current_chrom)
                current_chrom = next_chrom
            file.seek(0, 2)
            chroms[-1] = file.tell()
            chrom_names.append(current_chrom)
        return chroms, chrom_names

    def run(self) -> None:
        dyad_chroms, self.dyad_chrom_names = self.extract_chrom_names(self.dyad_file)
        mut_chroms, self.mutations_chrom_names = self.extract_chrom_names(self.mutation_file)

        if self.mutations_chrom_names != self.dyad_chrom_names:
            print('NOT THE SAME')
            return

        with mp.Pool(mp.cpu_count()) as pool:
            results = []
            for i in range(len(mut_chroms) - 1):
                dyad_start, dyad_end = dyad_chroms[i], dyad_chroms[i+1]
                mut_start, mut_end = mut_chroms[i], mut_chroms[i+1]
                result = pool.apply_async(self.process_block, (dyad_start, dyad_end, mut_start, mut_end), error_callback=lambda e: self.handle_error(e, i))
                results.append(result)

            for result in results:
                result.wait()

            pool.close()
            pool.join()

            for result in results:
                block_counts = result.get()
                for i in range(-1000, 1001):
                    for context in self.context_list:
                        self.counts[i][context] += block_counts[i][context]

        self.results_to_file()

        return self.output_file