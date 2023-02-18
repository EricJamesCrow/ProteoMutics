from pathlib import Path
import pandas as pd
import multiprocessing as mp

class DyadFastaCounter:

    def __init__(self, file: Path) -> None:
        self.path = file
        self.results = []
        self.final_counts = {}
        self.percentages = {}
        for i in range(-500,501):
            self.final_counts.setdefault(i, [0,0,0,0,0])
        self.pool = mp.Pool(mp.cpu_count())

    def run(self):
        
        # creates processes for each entry
        self.create_counting_per_line(self.path)  
        
        # closes the pool of processes and runs them. Then waits for processes to finish
        self.pool.close()
        self.pool.join()

        # collects results from each process and combines them into one dictionary
        for r in self.results: self.merge_dicts(self.final_counts, r[1])

        # converts the dictionary self.final_counts 
        self.calculate_percentages()

        # writes the results to a file
        self.results_to_file()

    def create_counting_per_line(self, fasta_path):
        """reads through file and assigns functions async to process pool for Statistics.count_line() function

        Args:
            fasta_file (Path): .fa file from BedtoolsCommands.bedtools_getfasta()
        """

        # open the fasta file
        with open(fasta_path, 'r') as f:
            # creates a process ID for each event so you can track each individual output
            process_id = -1
            
            # reads the first line of the file into memory
            f.readline()

            while line:
                # checks for beginning of a line by checking for the 'chr' and adds the process to the pool
                if 'chr' in line:
                    process_id += 1
                    fasta_position = f.tell()
                    self.pool.apply_async(func = self.count_line, args=[process_id, fasta_file, fasta_position], callback = collect_result)
                    line = f.readline()

    def count_line(self, process_id: int, file: str, position:int):
        
        # creates a dictionary that will hold onto the nucleotide position and the counts of each nucleotide
        counts = {}
        for i in range(-500,501):
            counts.setdefault(i, [0,0,0,0,0])
        
        # counts the nucleotides at each position 
        with open(file, 'r') as f:
            f.seek(position)
            chromosome = f.readline().strip().upper()
            for i, base in zip(range(-500,501), chromosome):
                    if base == 'A': counts[i][0] += 1
                    elif base == 'C': counts[i][1] += 1
                    elif base == 'G': counts[i][2] += 1
                    elif base == 'T': counts[i][3] += 1
                    else: counts[i][4] += 1
            return (process_id, counts)

    def collect_result(self, result):
        """collects results from each function

        Args:
            result (list): list object from count_line() function
        """
        self.results.append(result)

    def merge_dicts(self, keep: dict, add: dict):
        """merges dictionaries by updating the 'keep' dictionary with the 'add' dictionary

        Args:
            keep (dict): dictionary containing the items you want to update
            add (dict): dictionary containing items you want to add to 'keep'

        Returns:
            dict: returns updated 'keep' dictionary
        """
        for k, v in add.items():
            keep[k] = v
        return keep

    def calculate_percentages(self):
        for i in range(-500,501):
            total = sum(counts[i])
            self.percentages[i] = []
            for counts in counts[i]:
                self.percentages[i].append(counts/total)

    def results_to_file(self):
        output_file = self.path.with_name(f'{self.path.stem}_counts.txt')
        with open(output_file, 'w') as o:
            df = pd.DataFrame.from_dict(self.percentages, orient='index', columns=['A','C','G','T','N'])
            df.to_csv(output_file, sep = '\t')
