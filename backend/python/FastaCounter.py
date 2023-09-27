import multiprocessing as mp
from pathlib import Path

class GenomeFastaCounter:
    def __init__(self, fasta_file: str, context_length: int):
        self.fasta_file = Path(fasta_file)
        self.context_length = context_length
        self.output_file = self.fasta_file.with_name(f'{self.fasta_file.stem}_{self.context_length}mer.counts')
        self.results = []
        self.genome_counts = {}
        self._pool = mp.Pool(mp.cpu_count())
        self._count_fasta_contexts()
        self._pool.close()
        self._pool.join()
        self._merge_results()
        self._results_to_file(self.output_file, self.genome_counts)

    @staticmethod
    def _count_chromosome(i: int, file: str, position: int, context_length: int):
        with open(file, 'r') as f:
            context_dict = {}
            f.seek(position)
            chromosome = f.readline().strip().upper()
            next_line = chromosome
            in_chromosome = True
            while next_line and in_chromosome:
                while len(chromosome) >= context_length:
                    context_dict[chromosome[:context_length]] = context_dict.setdefault(chromosome[:context_length], 0) + 1
                    chromosome = chromosome[1:]
                next_line = f.readline().strip().upper()
                if '>' in next_line:
                    in_chromosome = False
                else:
                    chromosome += next_line
            return (i, context_dict)

    def _collect_result(self, result):
        self.results.append(result)

    @staticmethod
    def _merge_dicts(keep: dict, add: dict):
        for k, v in add.items():
            keep[k] = keep.get(k, 0) + v
        return keep

    def _count_fasta_contexts(self):
        with open(self.fasta_file, 'r') as f:
            i = -1
            line = f.readline()
            while line:
                if '_' in line or 'M' in line:
                    line = f.readline()
                    continue
                if '>' in line[0]:
                    i += 1
                    chromosome_number = line.strip().split('>')[1]
                    fasta_position = f.tell()
                    self._pool.apply_async(func=self._count_chromosome, args=[i, self.fasta_file, fasta_position, self.context_length], callback=self._collect_result)
                line = f.readline()

    def _merge_results(self):
        for r in self.results:
            self._merge_dicts(self.genome_counts, r[1])

    @staticmethod
    def _results_to_file(output_file: str, genome_counts: dict) -> None:
        with open(output_file, 'w') as o:
            o.write('CONTEXTS\tCOUNTS\n')
            # Sort genome_counts by keys (contexts) before writing to the file
            for k, v in sorted(genome_counts.items()):
                o.write(f'{k}\t{v}\n')


counter = GenomeFastaCounter('/home/cam/Documents/genome_files/hg19/hg19.fa', 3)