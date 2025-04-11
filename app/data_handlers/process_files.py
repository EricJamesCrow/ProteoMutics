from pathlib import Path
from app.utils import tools
from app.logic import dyad_context_counter, fasta_counter
import pandas as pd
import subprocess
import shutil

class MutationFile:

    def __init__(self, filepath, fasta) -> None:
        self.filepath = Path(filepath)
        self.proteomutics_folder = None
        self.counts = None
        self.mut = None
        self.pre_processed = False
        self.fasta = Path(fasta)

    def pre_process(self):
        # For .mut scenario
        if self.filepath.suffix == '.mut':
            self.proteomutics_folder = self.filepath.parent
            self.mut = self.filepath
            self.counts = self.filepath.with_suffix('.counts')
            if self.mut.exists() and self.counts.exists():
                self.pre_processed = True
                return
            elif self.mut.exists and not self.counts.exists():
                self.counts = self.count_contexts_mut(self.mut)
                self.pre_processed = True
                return
        # For .vcf scenario
        elif self.filepath.suffix == '.vcf':
            self.proteomutics_folder = self.filepath.parent.joinpath(self.filepath.stem+'_proteomutics')
            self.mut = self.proteomutics_folder.joinpath(self.filepath.stem + '.mut')
            self.counts = self.proteomutics_folder.joinpath(self.filepath.stem + '.counts')

            # Create proteomutics folder if it doesn't exist and process files
            if not self.proteomutics_folder.exists():
                self.proteomutics_folder.mkdir()
                print('processing_files')
                self.process_file(self.filepath, self.fasta)
                print('counting_contexts')
                self.counts = self.count_contexts_mut()
                self.mut = self.proteomutics_folder.joinpath(self.filepath.stem + '.mut')
            elif self.proteomutics_folder.exists() and not self.mut.exists():
                self.process_file(self.filepath, self.fasta)
                self.counts = self.count_contexts_mut()
                self.mut = self.proteomutics_folder.joinpath(self.filepath.stem + '.mut')

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
                if 'chr' not in chrom: chrom = 'chr'+chrom
                base_0 = str(int(tsv[1])-2)
                base_1 = str(int(tsv[1])+1)
                new_line = '\t'.join([chrom, base_0, base_1, '.', '0', '+', f'{tsv[3]}>{tsv[4]}'])
                o.write(new_line+'\n')

        # Define the acceptable human chromosome names.
        human_chromosomes = set(['chr' + str(i) for i in range(1, 23)] + ['chrX'])  # Adjust if you're including 'chrY'

        context_intermediate = file.with_suffix('.context.tmp')
        _, getfasta_output = tools.bedtools_getfasta(file.with_suffix('.tmp'), fasta)

        with open(getfasta_output) as f, open(file.with_suffix('.tmp')) as i, open(context_intermediate, 'w') as o:
            for fasta_line, bed_line in zip(f, i):
                bed_info = bed_line.strip().split('\t')
                
                # Basic error checking for the bed_info array
                if len(bed_info) < 7:  # Adjust the number based on your expected bed file structure
                    print(f"Skipping malformed line in bed file: {bed_line.strip()}")
                    continue

                chrom = bed_info[0]
                if chrom not in human_chromosomes:
                    # Skip entries from unwanted chromosomes
                    continue

                fasta_context = fasta_line.strip()
                sequence = fasta_context.split('\t')[-1].upper()  # Assuming the sequence is the last element

                if 'N' in sequence:
                    # Skip sequences containing 'N'
                    continue

                # Confirm bed and FASTA data match
                # Your conditions for matching may vary; adjust as needed
                if not all(info in fasta_context for info in bed_info[:3]):
                    print(f'ERROR: BED {bed_info} and FASTA {fasta_context} do not match')
                    break

                # Additional check for your specific case
                if sequence == bed_info[6]:
                    print(f'ERROR: BED {bed_info} and FASTA {fasta_context} do not match')
                    break

                # Assuming 0-based coordinates; adjust indices and math as necessary for your data
                new_line = '\t'.join([
                    chrom,
                    str(int(bed_info[1]) + 1),  # Adjusting start position
                    str(int(bed_info[2]) - 1),  # Adjusting end position
                    bed_info[3],
                    bed_info[4],
                    bed_info[5],
                    sequence,
                    bed_info[6]  # Assuming this is another field you want to preserve
                ])
                o.write(new_line + '\n')

        # Sort the file
        print(str(context_intermediate))
        print(str(self.mut))
        command = f'sort -k1,1 -k2,2n -k3,3n {context_intermediate} > {self.mut}'
        subprocess.run(command, shell=True)
        
        # Cleanup the intermediate files
        context_intermediate.unlink()
        file.with_suffix('.tmp').unlink()
        getfasta_output.unlink()
    
    def count_contexts_mut(self):
        keys = tools.contexts_in_iupac('NNN')
        counts = {key: 0 for key in keys}
        with open(self.mut, 'r') as f:
            for line in f:
                tsv = line.strip().split('\t')
                context = tsv[6]
                counts[context] += 1
        
        df = pd.DataFrame(list(counts.items()), columns=['CONTEXTS', 'COUNTS'])
        df = df.sort_values(by='CONTEXTS')   
        df.to_csv(self.mut.with_suffix('.counts'), sep='\t', index=False)
        
        return self.mut.with_suffix('.counts')



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

        # Check various scenarios to avoid running DyadFastaCounter more than necessary
        nuc_exists = potential_nuc.exists()
        counts_exists = potential_counts.exists()
        is_bed_file = self.filepath.suffix == '.bed'

        if nuc_exists and not counts_exists:
            # Scenario: .nuc exists but .counts does not
            self.nuc = potential_nuc
            dyad_context_counter.DyadFastaCounter(self.nuc).run()  # Run once since .counts doesn't exist
            self.counts = potential_counts

        elif is_bed_file and not nuc_exists:
            # Scenario: Input is a .bed file and .nuc does not exist
            self.nuc = potential_nuc
            self.process_dyads(self.filepath, self.fasta)  # Process dyads as .nuc doesn't exist
            dyad_context_counter.DyadFastaCounter(self.nuc).run()  # Needs to run after processing dyads
            self.counts = potential_counts

        elif not is_bed_file and not counts_exists:
            # Scenario: Input is a .nuc file and .counts does not exist
            self.nuc = self.filepath
            dyad_context_counter.DyadFastaCounter(self.nuc).run()  # Run since .counts doesn't exist
            self.counts = potential_counts

        elif nuc_exists and counts_exists:
            # Scenario: both .nuc and .counts exist
            self.nuc = potential_nuc
            self.counts = potential_counts
            # No need to run DyadFastaCounter again since both files already exist

        self.truncate_nuc_file()
        self.pre_processed = True

    def truncate_nuc_file(self):
        """
        Truncate the .nuc file to only contain the first three columns.
        This function assumes that the .nuc file's columns are tab-separated.
        """
        truncated_file_path = self.nuc.with_suffix('.nuc.truncated')

        with open(self.nuc, 'r') as original_file, open(truncated_file_path, 'w') as truncated_file:
            for line in original_file:
                parts = line.strip().split('\t')  # Assuming the file is tab-delimited.
                truncated_line = '\t'.join(parts[:3]) + '\n'  # Selecting only the first three columns.
                truncated_file.write(truncated_line)
        
        # Replace the original .nuc file with the truncated version.
        shutil.move(truncated_file_path, self.nuc)

    def process_dyads(self, dyad_file, fasta):
        dyad_file = Path(dyad_file)

        # Adjust positions and write to a tmp file
        with open(dyad_file, 'r') as f, open(dyad_file.with_suffix('.tmp'), 'w') as o:
            for line in f:
                tsv = line.strip().split()
                midpoint = int(tsv[1]) + (int(tsv[2]) - int(tsv[1])) / 2
                rounded_midpoint = int(midpoint)
                new_start = str(int(rounded_midpoint) - 1001)
                new_end = str(int(rounded_midpoint) + 1002)
                # new_start = str(int(tsv[1]) - 1001)
                # new_end = str(int(tsv[2]) + 1001)
                if int(new_start) < 0: continue
                new_line_values = [tsv[0], new_start, new_end] + tsv[3:]
                o.write('\t'.join(new_line_values) + '\n')
        
        # Assuming you've defined 'dyad_file' and 'fasta' above
        human_chromosomes = set(['chr' + str(i) for i in range(1, 23)] + ['chrX'])  # Defining expected chromosome names

        context_intermediate = dyad_file.with_suffix('.context.tmp')
        _, getfasta_output = tools.bedtools_getfasta(dyad_file.with_suffix('.tmp'), fasta)

        with open(getfasta_output) as f, open(dyad_file.with_suffix('.tmp')) as i, open(context_intermediate, 'w') as o:
            for fasta_line, bed_line in zip(f, i):
                bed_info = bed_line.strip().split('\t')
                
                # Error checking: Ensure the bed_info array has the expected number of elements
                if len(bed_info) < 3:
                    print(f"Skipping malformed line in bed file: {bed_line.strip()}")
                    continue

                chrom = bed_info[0]
                if chrom not in human_chromosomes:
                    # Skip the chromosomes that are not in the expected list
                    continue

                fasta_context = fasta_line.strip().split('\t')[-1]
                if 'N' in fasta_context.upper():
                    # Skip sequences with 'N'
                    continue

                # Assuming your coordinates are 0-based and you're adjusting by 1001
                original_start = str(int(bed_info[1]) + 1001)
                original_end = str(int(bed_info[2]) - 1001)

                new_line_values = [chrom, original_start, original_end, fasta_context.upper()]
                new_line = '\t'.join(new_line_values)
                o.write(new_line + '\n')
        
        # Sort the resulting file
        command = f'sort -k1,1 -k2,2n -k3,3n {context_intermediate} > {self.nuc}'
        subprocess.run(command, shell=True)
        
        # count contexts for the dyad file and create the counts file
        dyad_context_counter.DyadFastaCounter(self.nuc).run()
        self.counts = self.filepath.with_suffix('.counts')

        # Cleanup the intermediate files
        dyad_file.with_suffix('.tmp').unlink()
        context_intermediate.unlink()
        getfasta_output.unlink()



class FastaFile:

    def __init__(self, filepath) -> None:
        self.filepath = Path(filepath)
        self.counts = self.filepath.with_suffix('.counts')
        self.index = self.filepath.with_suffix('.fa.fai')
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