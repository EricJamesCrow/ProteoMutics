import multiprocessing as mp
import pandas as pd
from pathlib import Path
from ..utils import Tools
import traceback

class DyadFastaCounter:
    def __init__(self, file: str | Path, nucleomutics_folder, filename) -> None:
        self.path = Path(file)
        filename = Path(filename)
        nucleomutics_folder = Path(nucleomutics_folder)
        self.output_dir = Path(nucleomutics_folder)
        self.context_list = Tools.contexts_in_iupac('NNN')
        self.counts = self.initialize_counts(self.context_list)
        self.results = []
        self.output_file = nucleomutics_folder.joinpath(filename.with_suffix('.counts').name)

    @staticmethod
    def initialize_counts(context_list: list) -> dict:
        return {i: {key: 0 for key in context_list} for i in range(-1000, 1001)}

    @staticmethod
    def handle_error(error: Exception, task_id: int) -> None:
        print(f"Error in process {task_id}: {error}")
        traceback.print_tb(error.__traceback__)

    def results_to_file(self, context_list: list, counts: dict) -> None:
        df = pd.DataFrame.from_dict(counts, orient='index')
        df.columns = context_list
        df.index.name = 'Position'
        df.to_csv(self.output_file, sep='\t')

    def process_block(self, start_pos: int, end_pos: int) -> dict:
        counts = self.initialize_counts(self.context_list)
        with open(self.path) as f:
            f.seek(start_pos)
            while not end_pos or f.tell() < end_pos:
                line = f.readline()
                if not line:
                    break
                sequence = line.split("\t")[1].upper().strip()
                counts = self.update_counts(sequence, counts)
        return counts

    def update_counts(self, sequence: str, counts: dict) -> dict:
        for i in range(-1000, 1001):
            context = sequence[i+1000 : i + 1003]
            if context not in self.context_list:
                raise ValueError(f"Error in process {mp.current_process().pid}: Invalid context {context} at position {i}")
            counts[i][context] += 1
        return counts

    def run(self) -> None:
        num_blocks = mp.cpu_count()
        with mp.Pool(num_blocks) as pool:
            end_pos = self.get_file_end_position()
            block_positions = self.get_block_positions(num_blocks, end_pos)

            results = []
            for i in range(num_blocks):
                start_pos = block_positions[i]
                end_pos = block_positions[i+1]
                result = pool.apply_async(self.process_block, (start_pos, end_pos), error_callback=lambda e: self.handle_error(e, i))
                results.append(result)

            self.aggregate_results(results)
            self.results_to_file(self.context_list, self.counts)
        return self.output_file

    def get_file_end_position(self) -> int:
        with open(self.path) as f:
            f.seek(0, 2)
            return f.tell()

    def get_block_positions(self, num_blocks: int, end_pos: int) -> list:
        with open(self.path) as f:
            bytes_per_block = end_pos // num_blocks
            block_positions = [0]
            for i in range(1, num_blocks):
                f.seek(bytes_per_block * i)
                f.readline()
                block_positions.append(f.tell())
            block_positions.append(None)
        return block_positions

    def aggregate_results(self, results: list) -> None:
        for result in results:
            block_counts = result.get()
            for i in range(-1000, 1001):
                for context in self.context_list:
                    self.counts[i][context] += block_counts[i][context]
