from pathlib import Path
import python.PreProcessing as PreProcessing

def check_if_pre_processed(file_path: Path, typ: str):
    directory = file_path.parent
    folder_name = file_path.stem+'_Nucleomutics'
    if typ == 'mutation': 
        if directory / folder_name / file_path.with_suffix('.mut').exists():
            return True
    elif typ == 'nucleosome':
        if directory / folder_name / file_path.with_suffix('.mut').exists():
            return True
    elif typ == 'fasta':
        if directory / file_path.with_suffix('.fai').exists():
            return True
    return False

def pre_process_mutation_file(file_path: Path, fasta_file: Path):
    directory = file_path.parent
    nucleomutics_folder = directory / file_path.stem+'_Nucleomutics'
    temp_folder = directory / '.intermediate_files'
    nucleomutics_folder.mkdir()
    temp_folder.mkdir()
    step_1 = PreProcessing.vcf_snp_to_intermediate_bed(file_path, temp_folder)
    step_2 = PreProcessing.expand_context_custom_bed(step_1, fasta_file, temp_folder)
    step_3 = PreProcessing.filter_acceptable_chromosomes(step_2, temp_folder)
    _, step_4 = PreProcessing.check_and_sort(step_3, nucleomutics_folder, '.mut')
    temp_folder.rmdir()
    return step_4

def pre_process_nuc_map():
    pass

def pre_process_fasta():
    str = 'samtools faidx'
    pass

def check_for_results():
    pass