from pathlib import Path
from app.utils import tools
from app.logic import dyad_context_counter, fasta_counter
import pandas as pd
import subprocess

class MutationFile:

    def __init__(self, filepath, fasta) -> None:
        self.filepath = Path(filepath)
        self.counts = None
        self.mut = None
        self.proteomutics_folder = None
        self.pre_processed = False
        self.fasta = Path(fasta)

    def pre_process(self):
        # For .mut scenario
        if self.filepath.suffix == '.mut':
            self.mut = self.filepath
            self.proteomutics_folder = self.filepath.parent.joinpath(f"{self.filepath.stem}_proteomutics")

            potential_counts = self.proteomutics_folder.joinpath(f"{self.filepath.stem}.counts")

            if not potential_counts.exists():
                self.counts = self.count_contexts_mut(self.filepath)
            else:
                self.counts = potential_counts

        # For .vcf scenario
        elif self.filepath.suffix == '.vcf':
            self.proteomutics_folder = self.filepath.parent.joinpath(f"{self.filepath.stem}_proteomutics")
            
            potential_mut = self.proteomutics_folder.joinpath(f"{self.filepath.stem}.mut")
            potential_counts = self.proteomutics_folder.joinpath(f"{self.filepath.stem}.counts")

            # Create proteomutics folder if it doesn't exist and process files
            if not self.proteomutics_folder.exists():
                self.proteomutics_folder.mkdir()
                self.process_file(self.filepath, self.fasta)
                self.counts = self.count_contexts_mut(potential_mut)
                self.mut = potential_mut
            else:
                self.mut = potential_mut if potential_mut.exists() else None
                self.counts = potential_counts if potential_counts.exists() else self.count_contexts_mut(self.filepath)

        self.pre_processed = True

    def process_file(self, file, fasta):
        file = Path(file)
        # Convert VCF to intermediate BED format
        with open(file) as f, open(file.with_suffix('.tmp'), 'w') as o:
            for line in f:
                if line[0] == '#': continue
                tsv = line.strip().split('\t')
                if not (len(tsv[3]) == 1 and len(tsv[4]) == 1 and tsv[3] in 'ACGT' and tsv[4] in 'ACGT'): continue
                chrom = tsv[0]
                base_0 = str(int(tsv[1])-2)
                base_1 = str(int(tsv[1])+1)
                new_line = '\t'.join([chrom, base_0, base_1, '.', '0', '+', f'{tsv[3]}>{tsv[4]}'])
                o.write(new_line+'\n')

        # Filter and expand context
        human = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X', 'Y']
        context_intermediate = file.with_suffix('.context.tmp')
        _, getfasta_output = tools.bedtools_getfasta(file.with_suffix('.tmp'), fasta)
        with open(getfasta_output) as f, open(file.with_suffix('.tmp')) as i, open(context_intermediate, 'w') as o:
            for fasta_line, bed_line in zip(f, i):
                bed_info = bed_line.strip().split('\t')
                chrom = bed_info[0]
                filtered_chrom = ''.join([c for c in chrom if c in human])
                if filtered_chrom not in human:
                    continue

                fasta_context = fasta_line.strip().split('\t')[-1]
                if 'N' in fasta_context.upper():
                    continue

                if not all(info in fasta_context for info in bed_info[:3]):
                    print(f'ERROR: BED {bed_info} and FASTA {fasta_context} do not match')
                    break

                new_line = '\t'.join([bed_info[0], str(int(bed_info[1])+1), str(int(bed_info[2])-1), bed_info[3], bed_info[4], bed_info[5], fasta_context.upper(), bed_info[6]])
                o.write(new_line+'\n')

        # Sort the file
        command = f'sort -k1,1 -k2,2n -k3,3n -k6,6 {context_intermediate} > {self.mut}'
        subprocess.run(command, shell=True)
        
        # Cleanup the intermediate files
        context_intermediate.unlink()
        file.with_suffix('.tmp').unlink()
    
    def count_contexts_mut(file):
        file = Path(file)
        keys = tools.contexts_in_iupac('NNN')
        counts = {key: 0 for key in keys}
        with open(file, 'r') as f:
            for line in f:
                tsv = line.strip().split('\t')
                context = tsv[6]
                counts[context] += 1
        
        df = pd.DataFrame(list(counts.items()), columns=['CONTEXTS', 'COUNTS'])
        df = df.sort_values(by='CONTEXTS')   
        df.to_csv(file.with_suffix('.counts'), sep='\t', index=False)
        
        return file.with_suffix('.counts')



class DyadFile:

    def __init__(self, filepath, fasta) -> None:
        self.filepath = Path(filepath)
        self.counts = None
        self.nuc = None
        self.proteomutics_folder = None
        self.temp_folder = self.filepath.parent.joinpath('.intermediate_files')
        self.pre_processed = False
        self.fasta = Path(fasta)

    def pre_process(self):
        # Define the potential .nuc and .counts paths for both cases (.bed or .nuc input)
        if self.filepath.suffix == '.bed':
            self.proteomutics_folder = self.filepath.parent.joinpath(self.filepath.stem+'_proteomutics')
            potential_nuc = self.proteomutics_folder.joinpath(self.filepath.stem + '.nuc')
        else:  # If the file is .nuc, it's expected to be inside the proteomutics folder
            self.proteomutics_folder = self.filepath.parent
            potential_nuc = self.filepath

        potential_counts = self.proteomutics_folder.joinpath(self.filepath.stem + '.counts')

        # Ensure the proteomutics folder is there
        if not self.proteomutics_folder.exists():
            self.proteomutics_folder.mkdir()

        # Scenario: .nuc exists but .counts does not
        if potential_nuc.exists() and not potential_counts.exists():
            self.nuc = potential_nuc
            dyad_context_counter.DyadFastaCounter(self.fasta, self.nuc).run()
            self.counts = potential_counts

        # Scenario: Input is a .bed file and .nuc does not exist
        elif self.filepath.suffix == '.bed' and not potential_nuc.exists():
            self.process_dyads(self.filepath, self.fasta)
            dyad_context_counter.DyadFastaCounter(self.fasta, self.nuc).run()
            self.counts = potential_counts

        # Scenario: Input is a .nuc file
        elif self.filepath.suffix == '.nuc':
            self.nuc = self.filepath
            if not potential_counts.exists():
                dyad_context_counter.DyadFastaCounter(self.fasta, self.nuc).run()
                self.counts = potential_counts

        self.pre_processed = True

    def process_dyads(self, dyad_file, fasta):
        dyad_file = Path(dyad_file)

        # Adjust positions and write to a tmp file
        with open(dyad_file, 'r') as f, open(dyad_file.with_suffix('.tmp'), 'w') as o:
            for line in f:
                tsv = line.strip().split()
                new_start = str(int(tsv[1]) - 1001)
                new_end = str(int(tsv[2]) + 1001)
                if int(new_start) < 0: continue
                new_line_values = [tsv[0], new_start, new_end] + tsv[3:]
                o.write('\t'.join(new_line_values) + '\n')
        
        # Get the FASTA context for the adjusted bed file
        human = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X', 'Y']
        context_intermediate = dyad_file.with_suffix('.context.tmp')
        _, getfasta_output = tools.bedtools_getfasta(dyad_file.with_suffix('.tmp'), fasta)
        with open(getfasta_output) as f, open(dyad_file.with_suffix('.tmp')) as i, open(context_intermediate, 'w') as o:
            for fasta_line, bed_line in zip(f, i):
                bed_info = bed_line.strip().split('\t')
                chrom = bed_info[0]
                filtered_chrom = ''.join([c for c in chrom if c in human])
                if filtered_chrom not in human:
                    continue

                fasta_context = fasta_line.strip().split('\t')[-1]
                if 'N' in fasta_context.upper():
                    continue

                original_start = str(int(bed_info[1]) + 1001)
                original_end = str(int(bed_info[2]) - 1001)
                new_line_values = [bed_info[0], original_start, original_end] + [fasta_context.upper()]
                new_line = '\t'.join(new_line_values)
                o.write(new_line + '\n')
        
        # Sort the resulting file
        command = f'sort -k1,1 -k2,2n -k3,3n {context_intermediate} > {self.nuc}'
        subprocess.run(command, shell=True)
        
        # count contexts for the dyad file and create the counts file
        dyad_context_counter.DyadFastaCounter(self.fasta, self.nuc).run()
        self.counts = self.filepath.with_suffix('.counts')

        # Cleanup the intermediate files
        dyad_file.with_suffix('.tmp').unlink()
        context_intermediate.unlink()



class FastaFile:

    def __init__(self, filepath) -> None:
        self.filepath = Path(filepath)
        self.counts = self.filepath.with_suffix('.counts')
        self.index = self.filepath.with_suffix('.fai')
        self.pre_processed = False

    def pre_process(self):
        if self.index.exists() and self.counts.exists():
            self.pre_processed = True
            return
        else:
            command = f'samtools faidx {self.filepath}'
            with subprocess.Popen(args=command, stdout=subprocess.PIPE, shell=True) as p:
                result = p.communicate()
            self.counts = fasta_counter.GenomeFastaCounter(self.filepath).run()
            self.pre_processed = True
            return