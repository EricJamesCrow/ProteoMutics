import multiprocessing as mp
import pandas as pd
from pathlib import Path

class DyadFastaCounter:

    def __init__(self, file: Path) -> None:
        self.path = file
        self.final_counts = mp.Manager().dict()
        for i in range(-500, 501):
            self.final_counts[i] = [0, 0, 0, 0, 0]

    def run(self):
        # Count sequences in parallel using a process pool
        with mp.Pool() as pool:
            with open(self.path, 'r') as f:
                pool.map(self.count_line, (line.strip().split('\t')[1].upper() for line in f))

        # Calculate percentages and write results to file
        self.calculate_percentages()
        self.results_to_file()

    def count_line(self, sequence: str):
        # counts the nucleotides at each position
        local_counts = {i: [0, 0, 0, 0, 0] for i in range(-500, 501)}
        for i, base in zip(range(-500, 501), sequence):
            if base == 'A':
                local_counts[i][0] += 1
            elif base == 'C':
                local_counts[i][1] += 1
            elif base == 'G':
                local_counts[i][2] += 1
            elif base == 'T':
                local_counts[i][3] += 1
            else:
                local_counts[i][4] += 1
        for i in range(-500, 501):
            for j in range(5):
                self.final_counts[i][j] += local_counts[i][j]

    def calculate_percentages(self) -> dict:
        percentages = {}
        for i in range(-500, 501):
            total = sum(self.final_counts[i])
            if total != 0:
                percentages[i] = []
                for temp_counts in self.final_counts[i]:
                    percentages[i].append("{:.6f}".format(temp_counts/total))
            else:
                print('ERROR!')
        self.percentages = percentages

    def results_to_file(self):
        output_file = self.path.with_name(f'{self.path.stem}_counts.txt')
        with open(output_file, 'w') as o:
            df = pd.DataFrame.from_dict(self.percentages, orient='index', columns=['A', 'C', 'G', 'T', 'Other'])
            df.to_csv(output_file, sep='\t')

if __name__ == '__main__':
    mp.freeze_support()
    fasta_counter = DyadFastaCounter(Path('src/models/test_counting_file.fa'))
    fasta_counter.run()
