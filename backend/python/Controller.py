from pathlib import Path
# from . import BedtoolsCommands
import BedtoolsCommands
import shutil
# from . import PreProcessing
import PreProcessing
# from . import DyadContextCounter
import DyadContextCounter
import subprocess

def check_if_pre_processed(file_path: Path, typ: str):
    print('Running folder check step for '+str(typ)+ ' file')
    directory = file_path.parent
    nucleomutics_folder = directory.joinpath(file_path.with_name(file_path.stem+'_nucleomutics').stem)
    print(nucleomutics_folder)
    # print(nucleomutics_folder)
    if typ == 'mutation': 
        check = nucleomutics_folder.joinpath(file_path.with_suffix('.mut').name)
        if check.exists():
            return True
    elif typ == 'nucleosome':
        check = nucleomutics_folder.joinpath(file_path.with_suffix('.nuc').name)
        if check.exists():
            return True
    elif typ == 'fasta':
        check = directory / file_path.with_suffix('.fai')
        if check.exists():
            return True
    return False

def pre_process_mutation_file(file_path: Path, fasta_file: Path):
    print('[Mutation]Pre-processing file')
    directory = file_path.parent
    nucleomutics_folder = directory.joinpath(file_path.with_name(file_path.stem+'_nucleomutics').stem)
    temp_folder = directory.joinpath('.intermediate_files')
    if nucleomutics_folder.exists():
        shutil.rmtree(nucleomutics_folder)
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
    nucleomutics_folder.mkdir()
    temp_folder.mkdir()
    print('[Mutation]Converting vcf to intermediate bed')
    step_1 = PreProcessing.vcf_snp_to_intermediate_bed(file_path, temp_folder)
    print('[Mutation]Expanding context of custom bed file')
    step_2 = PreProcessing.expand_context_custom_bed(step_1, fasta_file, temp_folder)
    print('[Mutation]Filtering non-canonical chromosomes')
    step_3 = PreProcessing.filter_acceptable_chromosomes(step_2, temp_folder)
    print('[Mutation]Checking and sorting file and converting to ProteoMutics format')
    _, new_mut = PreProcessing.check_and_sort(step_3, nucleomutics_folder, '.mut')
    shutil.rmtree(temp_folder)
    return new_mut

# change to save to program folder not input file directory
def pre_process_nucleosome_map(file_path: Path, fasta_file: Path):
    print('[Nucleosome]Pre-processing file')
    directory = file_path.parent
    nucleomutics_folder = directory.joinpath(file_path.with_name(file_path.stem+'_nucleomutics').stem)
    temp_folder = directory.joinpath('.intermediate_files')
    if nucleomutics_folder.exists():
        shutil.rmtree(nucleomutics_folder)
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
    nucleomutics_folder.mkdir()
    temp_folder.mkdir()
    print('[Nucleosome]Adjusting dyad positions')
    step_1 = PreProcessing.adjust_dyad_positions(file_path, temp_folder)
    print('[Nucleosome]Running bedtools getfasta')
    step_2 = BedtoolsCommands.bedtools_getfasta(step_1, fasta_file)
    print('[Nucleosome]Filtering lines with N')
    step_3, fasta = PreProcessing.filter_lines_with_n(Path(step_2[1]), file_path, temp_folder)
    print('[Nucleosome]Filtering non-canonical chromosomes')
    step_4 = PreProcessing.filter_acceptable_chromosomes(step_3, temp_folder)
    print('[Nucleosome]Checking and sorting file and converting to ProteoMutics format')
    _, new_dyad = PreProcessing.check_and_sort(step_4, nucleomutics_folder, '.nuc')
    new_dyad = PreProcessing.final_nuc_rename(new_dyad, file_path.with_suffix('.nuc').name)
    print('[Nucleosome]Counting dyad contexts')
    counts = DyadContextCounter.DyadFastaCounter(fasta, nucleomutics_folder)
    shutil.rmtree(temp_folder)
    print('[Nucleosome]Finished file')
    return new_dyad, counts


def pre_process_fasta(fasta_file: Path):
    command = f'samtools faidx {fasta_file}'
    with subprocess.Popen(args=command, stdout=subprocess.PIPE, shell=True) as p:
        result = p.communicate()
    pass

def check_for_results():
    pass