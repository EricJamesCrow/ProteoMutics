from pathlib import Path
import pandas as pd
import multiprocessing as mp

class DyadFastaCounter:

    def __init__(self, file: Path) -> None:
        self.path = file
        self.final_counts = {}
        self.percentages = {}
        self.results = []
        for i in range(-500, 501):
            self.final_counts.setdefault(i, [0,0,0,0])

    def run(self):
        # Count sequences in parallel using a process pool
        with mp.Pool() as pool:
            with open(self.path, 'r') as f:
                counts = pool.map(self.count_line, (line.strip().split('\t')[1].upper() for line in f))

        # Combine results from all processes
        for c in counts:
            self.final_counts = self.merge_dicts(self.final_counts, c)

        # Calculate percentages and write results to file
        self.calculate_percentages()
        self.results_to_file()

    def count_line(self, sequence: str):
        # creates a dictionary that will hold onto the nucleotide position and the counts of each nucleotide
        counts = {}
        for i in range(-500, 501):
            counts.setdefault(i, [0, 0, 0, 0])

        # counts the nucleotides at each position
        for i, base in zip(range(-500, 501), sequence):
            if base == 'A':
                counts[i][0] += 1
            elif base == 'C':
                counts[i][1] += 1
            elif base == 'G':
                counts[i][2] += 1
            elif base == 'T':
                counts[i][3] += 1
            else:
                counts[i][4] += 1

        # return counts
        return counts

    def merge_dicts(self, keep: dict, add: dict):
        for k, v in add.items():
            for i in range(len(v)):
                keep[k][i] += v[i]
        return keep

    def calculate_percentages(self) -> dict:
        for i in range(-500, 501):
            total = sum(self.final_counts[i])
            if total != 0:
                self.percentages[i] = []
                for temp_counts in self.final_counts[i]:
                    self.percentages[i].append("{:.6f}".format(temp_counts/total))
            else:
                print('ERROR!')

    def results_to_file(self):
        output_file = self.path.with_name(f'{self.path.stem}_counts.txt')
        with open(output_file, 'w') as o:
            df = pd.DataFrame.from_dict(self.percentages, orient='index', columns=['A','C','G','T'])
            print(df)
            df.to_csv(output_file, sep = '\t')


if __name__ == '__main__':
    mp.freeze_support()
    fasta_counter = DyadFastaCounter(Path('src/models/test_counting_file.fa'))
    fasta_counter.run()
