import multiprocessing as mp  # Importing multiprocessing for parallel computing.
import pandas as pd  # Importing pandas for data manipulation and analysis.
from pathlib import Path  # Importing Path from pathlib for object-oriented filesystem paths.
from . import Tools  # Importing Tools from the current directory.
import traceback  # Importing traceback to print stack traces.
from typing import Tuple, List  # Importing Tuple and List from typing for type hinting.


class MutationIntersector:
    
    def __init__(self, mutation_file: Path, dyad_file: Path, output_file: Path) -> None:
        self.output_file = output_file
        self.mutation_file = mutation_file  # Initializing mutation_file attribute.
        self.dyad_file = dyad_file  # Initializing dyad_file attribute.
        self.context_list = Tools.contexts_in_iupac('NNN')  # Calling contexts_in_iupac method from Tools and passing 'NNN' as argument.
        # Initializing counts attribute as a dictionary with keys from -1000 to 1000, each having a nested dictionary derived from context_list.
        self.counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        self.results = []  # Initializing results attribute as an empty list.
        # Constructing output_file attribute using mutation_file's name and dyad_file's stem and appending '_intersected_mutations_counts.txt' to it.
        try:
            self.output_file = mutation_file.with_name(f'{mutation_file.stem}_{dyad_file.stem}_intersected_mutations_counts.txt')
        except:
            print(mutation_file)
        self.dyad_chrom_names = []  # Initializing dyad_chrom_names attribute as an empty list.
        self.mutations_chrom_names = []  # Initializing mutations_chrom_names attribute as an empty list.
        self.run()  # Calling run method.

    def handle_error(self, error: Exception, task_id: int) -> None:  # Defining handle_error method to handle errors.
        print(f"Error in process {task_id}: {error}")  # Printing error message.
        traceback.print_tb(error.__traceback__)  # Printing stack trace of the error.

    def results_to_file(self, context_list: list, counts: dict, output_file: Path) -> None:  # Defining results_to_file method to write results into a file.
        df = pd.DataFrame.from_dict(counts, orient='index')  # Creating a DataFrame from counts dictionary.
        df.columns = context_list  # Setting DataFrame columns using context_list.
        df.index.name = 'Position'  # Naming DataFrame index as 'Position'.
        df.to_csv(output_file, sep='\t')  # Writing DataFrame to output_file in tab-separated format.

    def process_block(self, dyad_start_position: int, dyad_end_position: int, mut_start_position: int, mut_end_position: int, context_list: list, mutation_file_path: Path, dyad_file_path: Path, process_id: int) -> List[Tuple[int, dict]]:
        # Initializing a dictionary similar to the one in __init__ to store counts.
        counts = {i: {key: 0 for key in context_list} for i in range(-1000,1001)}
        with open(dyad_file_path) as dyad_file, open(mutation_file_path) as mut_file:  # Opening both dyad and mutation files.
            dyad_file.seek(dyad_start_position)  # Moving dyad_file's read/write pointer to dyad_start_position.
            mut_file.seek(mut_start_position)  # Moving mut_file's read/write pointer to mut_start_position.
            jump_back_position = mut_start_position  # Storing mut_start_position in jump_back_position.
            mut_data = mut_file.readline().strip().split('\t')  # Reading a line from mut_file, stripping whitespaces, splitting it by tabs, and storing in mut_data.
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
        self.results_to_file(self.context_list, self.counts, self.output_file)

        return self.output_file
