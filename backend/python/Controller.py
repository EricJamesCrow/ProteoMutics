from pathlib import Path
from . import BedtoolsCommands
import shutil
from . import PreProcessing

def check_if_pre_processed(file_path: Path, typ: str):
    directory = file_path.parent
    nucleomutics_folder = directory.joinpath(file_path.with_name(file_path.stem+'_nucleomutics').stem)
    print(nucleomutics_folder)
    if typ == 'mutation': 
        check = nucleomutics_folder.joinpath(file_path.with_suffix('.mut').name)
        print(check)
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
    directory = file_path.parent
    nucleomutics_folder = directory.joinpath(file_path.with_name(file_path.stem+'_nucleomutics').stem)
    temp_folder = directory.joinpath('.intermediate_files')
    if nucleomutics_folder.exists():
        shutil.rmtree(nucleomutics_folder)
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
    nucleomutics_folder.mkdir()
    temp_folder.mkdir()
    step_1 = PreProcessing.vcf_snp_to_intermediate_bed(file_path, temp_folder)
    step_2 = PreProcessing.expand_context_custom_bed(step_1, fasta_file, temp_folder)
    step_3 = PreProcessing.filter_acceptable_chromosomes(step_2, temp_folder)
    _, step_4 = PreProcessing.check_and_sort(step_3, nucleomutics_folder, '.mut')
    shutil.rmtree(temp_folder)
    return step_4

def pre_process_nuc_map(file_path: Path, fasta_file: Path):
    directory = file_path.parent
    nucleomutics_folder = directory.joinpath(file_path.with_name(file_path.stem+'_nucleomutics').stem)
    temp_folder = directory.joinpath('.intermediate_files')
    if nucleomutics_folder.exists():
        shutil.rmtree(nucleomutics_folder)
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
    nucleomutics_folder.mkdir()
    temp_folder.mkdir()
    step_1 = PreProcessing.adjust_dyad_positions(file_path, temp_folder)
    step_2 = BedtoolsCommands.bedtools_getfasta(step_1, fasta_file)
    # step_3 = 

def pre_process_fasta():
    str = 'samtools faidx'
    pass

def check_for_results():
    pass