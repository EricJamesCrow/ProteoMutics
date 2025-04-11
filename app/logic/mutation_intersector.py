from app.utils import tools
import multiprocessing as mp
import pandas as pd
from pathlib import Path
import traceback


class MutationIntersector:
    
    def __init__(self, mutation_file: Path | str, dyad_file: Path | str, mut_context='NNN', mutation_type='G>T') -> None:
        self.mutation_file = Path(mutation_file)
        self.dyad_file = Path(dyad_file)
        self.output_file = mutation_file.with_name(f'{mutation_file.stem}_{dyad_file.stem}.intersect')
        self.flipped_output_file = mutation_file.with_name(f'{mutation_file.stem}_{dyad_file.stem}_flipped.intersect')  # added this line for flipped counts output
        self.mut_context = tools.contexts_in_iupac(mut_context)
        self.mutation_type = tools.mutation_combinations(mutation_type)
        self.rev_mutation_type = tools.mutation_combinations(tools.reverse_complement(mutation_type[0])+">"+tools.reverse_complement(mutation_type[2]))
        self.context_list = tools.contexts_in_iupac('NNN')

        self.counts = self.initialize_counts()
        self.flipped_counts = self.initialize_counts()  # initializing flipped_counts
        self.results = []
        self.dyad_chrom_names = []
        self.mutations_chrom_names = []

    def initialize_counts(self) -> dict:
        return {i: {key: 0 for key in self.context_list} for i in range(-1000, 1001)}

    @staticmethod
    def handle_error(error: Exception, task_id: int) -> None:
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def flipped_results_to_file(self) -> None:
        df = pd.DataFrame.from_dict(self.flipped_counts, orient='index')
        df.columns = self.context_list
        df.index.name = 'Position'
        df.to_csv(self.flipped_output_file, sep='\t')

    def results_to_file(self) -> None:
        df = pd.DataFrame.from_dict(self.counts, orient='index')
        df.columns = self.context_list
        df.index.name = 'Position'
        df.to_csv(self.output_file, sep='\t')

    def determine_if_flip_context(self, mutation: str, strand: str, context: str) -> str:
        if mutation in self.rev_mutation_type:
            if tools.reverse_complement(context) in self.mut_context:
                return True
        else:
            return False

    def process_block(self, dyad_start_position: int, dyad_end_position: int, mut_start_position: int, mut_end_position: int) -> dict:
        # Initializing a dictionary similar to the one in __init__ to store counts.
        counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        flipped_counts = {i: {key: 0 for key in self.context_list} for i in range(-1000,1001)}
        with open(self.dyad_file) as dyad_file, open(self.mutation_file) as mut_file:  # Opening both dyad and mutation files.
            dyad_file.seek(dyad_start_position)  # Moving dyad_file's read/write pointer to dyad_start_position.
            mut_file.seek(mut_start_position)  # Moving mut_file's read/write pointer to mut_start_position.
            jump_back_position = mut_start_position  # Storing mut_start_position in jump_back_position.
            mut_data = mut_file.readline().strip().split('\t')  # Reading a line from mut_file, stripping whitespaces, splitting it by tabs, and storing in mut_data.
            while mut_data[6] not in self.mut_context and mut_data[7] not in self.mutation_type:
                mut_data = mut_file.readline().strip().split('\t')
            
            mut_start = int(mut_data[1])  # Converting second item of mut_data to integer and storing in mut_start.
            
            context = mut_data[6]
            mutation = mut_data[7]
            strand = mut_data[5]
            
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
                    
                    context = mut_data[6]   # Storing sixth item of mut_data in context.
                    mutation = mut_data[7]
                    strand = mut_data[5]

                # This loop checks if the mutation start position is within a 1000 base pairs range from the dyad start position. If it is, it increments the count for the context of that mutation.
                while -1000 <= mut_start-dyad_start <= 1000:
                    if self.determine_if_flip_context(mutation, strand, context):
                        counts[mut_start-dyad_start][context] += 1
                        flipped_counts[dyad_start-mut_start][tools.reverse_complement(context)] += 1
                    else:
                        counts[mut_start-dyad_start][context] += 1
                        flipped_counts[mut_start-dyad_start][context] += 1

                    mut_data = mut_file.readline().strip().split('\t')
                    if mut_file.tell() > mut_end_position:
                        break
                    if mut_data == ['']:
                        break
                    
                    mut_start = int(mut_data[1])

                    context = mut_data[6]   # Storing sixth item of mut_data in context.
                    mutation = mut_data[7]
                    strand = mut_data[5]

                # Here, it sets the pointer of the mutation file back to the start of the previous dyad.
                mut_file.seek(jump_back_position)
                mut_data = mut_file.readline().strip().split('\t')
                if mut_file.tell() > mut_end_position:
                    break
                if mut_data == ['']:
                    break
                
                mut_start = int(mut_data[1])

                context = mut_data[6]   # Storing sixth item of mut_data in context.
                mutation = mut_data[7]
                strand = mut_data[5]
                
        return counts, flipped_counts

    def extract_chrom_positions(self, file_path: Path):
        chrom_positions = {}
        with open(file_path, 'r') as file:
            start_pos = 0
            current_chrom = None
            while True:
                location = file.tell()
                line = file.readline()
                if not line:  # Check for EOF
                    if current_chrom is not None:
                        # Assign the last position when EOF is reached
                        chrom_positions[current_chrom] = (start_pos, location)
                    break  # Exit the loop at EOF
                next_chrom, *_ = line.strip().split('\t')
                if current_chrom and current_chrom != next_chrom:
                    chrom_positions[current_chrom] = (start_pos, location)
                    start_pos = location
                current_chrom = next_chrom
        return chrom_positions
    
    def run(self) -> None:
        # Extract chromosome positions from the files
        dyad_positions = self.extract_chrom_positions(self.dyad_file)
        mutation_positions = self.extract_chrom_positions(self.mutation_file)

        # Find the common chromosomes
        common_chroms = set(dyad_positions).intersection(mutation_positions)
        if not common_chroms:
            print('No common chromosomes found.')
            return
        else:
            sorted_common_chroms = sorted(common_chroms)
            print(f'Found {len(common_chroms)} common chromosomes: {sorted_common_chroms}')

        # Process the blocks in parallel
        with mp.Pool() as pool:
            results = []
            # Process all common chromosome ranges
            for chrom in sorted_common_chroms:
                dyad_start, dyad_end = dyad_positions[chrom]
                mut_start, mut_end = mutation_positions[chrom]
                result = pool.apply_async(self.process_block, (dyad_start, dyad_end, mut_start, mut_end),
                                          error_callback=lambda e, chrom=chrom: self.handle_error(e, chrom))
                results.append(result)

            # Collect results
            for result in results:
                result.wait()

            pool.close()
            pool.join()

        # Process results as before
        for result in results:
            block_counts, block_flipped_counts = result.get()
            for i in range(-1000, 1001):
                for context in self.context_list:
                    self.counts[i][context] += block_counts[i][context]
                    self.flipped_counts[i][context] += block_flipped_counts[i][context]  # accumulate flipped_counts

        self.results_to_file()
        self.flipped_results_to_file()

        return self.output_file