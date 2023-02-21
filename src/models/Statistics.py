from pathlib import Path
import pandas as pd
import multiprocessing as mp
import sys

class DyadFastaCounter:

    def __init__(self, file: Path) -> None:
        self.path = file
        self.results = []
        self.final_counts = {}
        self.percentages = {}
        self.process_counter = 0
        for i in range(-500,501):
            self.final_counts.setdefault(i, [0,0,0,0,0])
        self.pool = mp.Pool(mp.cpu_count())

    def run(self):
        
        # creates processes for each entry
        self.create_counting_per_line(self.path)

        # closes the pool of processes and runs them. Then waits for processes to finish
        self.pool.close()
        self.pool.join()

        # converts the dictionary self.final_counts 
        print(self.results)
        for counts in self.results:
            self.final_counts = self.merge_dicts(self.final_counts, counts)
        # print(self.final_counts)


    def create_counting_per_line(self, fasta_path):
        """reads through file and assigns functions async to process pool for Statistics.count_line() function

        Args:
            fasta_file (Path): .fa file from BedtoolsCommands.bedtools_getfasta()
        """

        # open the fasta file
        with open(fasta_path, 'r') as f:
            # reads the first line of the file into memory
            for line in f:
                try:
                    # checks for beginning of a line by checking for the 'chr' and adds the process to the pool
                    tsv = line.strip().split('\t')
                    sequence = tsv[1].upper()
                    self.pool.apply_async(func=self.count_line, args=[sequence], callback=self.collect_result)
                    # prints how many processses it's counting
                    # self.process_counter += 1
                    # sys.stdout.write(f'Processed {self.process_counter} lines\r')
                    # sys.stdout.flush()
                except Exception as e:
                    print(f"Error processing line {self.process_counter}: {e}")

    def count_line(self, sequence: str):
        # creates a dictionary that will hold onto the nucleotide position and the counts of each nucleotide
        counts = {}
        for i in range(-500, 501):
            counts.setdefault(i, [0, 0, 0, 0, 0])

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

    def collect_result(self, counts):
        self.results.append(counts)

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
                    self.percentages[i].append(temp_counts/total)
            else:
                self.percentages[i] = [0.25, 0.25, 0.25, 0.25, 0.0]

    def results_to_file(self):
        output_file = self.path.with_name(f'{self.path.stem}_counts.txt')
        with open(output_file, 'w') as o:
            df = pd.DataFrame.from_dict(self.percentages, orient='index', columns=['A','C','G','T','N'])
            print(df)
            df.to_csv(output_file, sep = '\t')
