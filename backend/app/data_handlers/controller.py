from . import pre_processing
from app.logic import dyad_context_counter, fasta_counter

from pathlib import Path
from utils import Tools
import shutil
import subprocess

def check_if_pre_processed(file_path: Path | str, typ: str):
    file_path = Path(file_path)
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
        check = directory.joinpath(file_path.with_name(f'{file_path.stem}_3mer.counts'))
        if check.exists():
            return True
    return False

def pre_process_mutation_file(file_path: Path | str, fasta_file: Path | str):
    file_path = Path(file_path)
    fasta_file = Path(fasta_file)
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
    step_1 = pre_processing.vcf_snp_to_intermediate_bed(file_path, temp_folder)
    print('[Mutation]Expanding context of custom bed file')
    step_2 = pre_processing.expand_context_custom_bed(step_1, fasta_file, temp_folder)
    print('[Mutation]Filtering non-canonical chromosomes')
    step_3 = pre_processing.filter_acceptable_chromosomes(step_2, temp_folder)
    print('[Mutation]Checking and sorting file and converting to ProteoMutics format')
    _, new_mut = pre_processing.check_and_sort(step_3, nucleomutics_folder, '.mut')
    shutil.rmtree(temp_folder)
    return new_mut

def pre_process_nucleosome_map(file_path: Path | str, fasta_file: Path | str):
    file_path = Path(file_path)
    fasta_file = Path(fasta_file)   
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
    step_1 = pre_processing.adjust_dyad_positions(file_path, temp_folder)
    print('[Nucleosome]Running bedtools getfasta')
    step_2 = Tools.bedtools_getfasta(step_1, fasta_file)
    print('[Nucleosome]Filtering lines with N')
    step_3, fasta = pre_processing.filter_lines_with_n(Path(step_2[1]), file_path, temp_folder)
    print('[Nucleosome]Filtering non-canonical chromosomes')
    step_4 = pre_processing.filter_acceptable_chromosomes(step_3, temp_folder)
    print('[Nucleosome]Checking and sorting file and converting to ProteoMutics format')
    _, new_dyad = pre_processing.check_and_sort(step_4, nucleomutics_folder, '.nuc')
    new_dyad = pre_processing.final_nuc_rename(new_dyad, file_path.with_suffix('.nuc').name)
    print('[Nucleosome]Counting dyad contexts')
    counts_file = dyad_context_counter.DyadFastaCounter(fasta, nucleomutics_folder=nucleomutics_folder, filename=new_dyad).run()
    print(counts_file)
    shutil.rmtree(temp_folder)
    print('[Nucleosome]Finished file')
    return new_dyad, counts_file

def pre_process_fasta(fasta_file: Path | str):
    fasta_file = Path(fasta_file)
    command = f'samtools faidx {fasta_file}'
    with subprocess.Popen(args=command, stdout=subprocess.PIPE, shell=True) as p:
        result = p.communicate()
    print('Counting genome contexts..')
    fasta_counter.GenomeFastaCounter(fasta_file).run()
    pass

def check_for_results():
    pass
