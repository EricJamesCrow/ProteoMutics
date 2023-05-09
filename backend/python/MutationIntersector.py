import multiprocessing as mp
import pandas as pd
from pathlib import Path
from . import Tools
import traceback
from typing import Tuple, List


class MutationIntersector:
    
    def __init__(self, mutation_file: Path, dyad_file: Path) -> None:
        self.mutation_file = mutation_file
        self.dyad_file = dyad_file
        self.context_list = Tools.contexts_in_iupac('NNN')
        self.counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        self.results = []
        self.output_file = mutation_file.with_name(f'{mutation_file.stem}_{dyad_file.stem}_intersected_mutations_counts.txt')
        self.dyad_chrom_names = []
        self.mutations_chrom_names = []
        self.run()

    def handle_error(self, error: Exception, task_id: int) -> None:
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def results_to_file(self, context_list: list, counts: dict, output_file: Path) -> None:
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
                # please speed me up
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
                # stop here
                
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

        return self.output_file
