import multiprocessing as mp
import pandas as pd
from pathlib import Path
import Tools

def df_division_and_standardization(mutation_counts: Path, dyad_counts: Path, iupac: str):
    mutations_df = pd.read_csv(mutation_counts, sep= '\t', index_col=0, header=0)
    dyads_df = pd.read_csv(dyad_counts, sep= '\t', index_col=0, header=0)
    contexts = Tools.contexts_in_iupac(iupac)
    all_contexts = contexts
    for item in contexts:
        rev_comp = Tools.reverse_complement(item)
        if rev_comp not in all_contexts:
            all_contexts.append(rev_comp)
    new_mut_df = mutations_df.loc[:,all_contexts]
    new_dyad_df = dyads_df.loc[:,all_contexts]
    results_dict = {}
    i = -1000
    for mut_index, mut_row in new_mut_df.iterrows():
        results_dict[i] = [(sum(mut_row.tolist())/sum(new_dyad_df.loc[mut_index].tolist()))]
        i += 1
    result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])
    result_df_normalized = result_df.divide(result_df.median())
    return result_df_normalized

def df_median_norm_raw_counts(mutation_counts: Path, iupac: str):
    mutations_df = pd.read_csv(mutation_counts, sep= '\t', index_col=0, header=0)
    contexts = Tools.contexts_in_iupac(iupac)
    all_contexts = contexts
    for item in contexts:
        rev_comp = Tools.reverse_complement(item)
        if rev_comp not in all_contexts:
            all_contexts.append(rev_comp)
    new_mut_df = mutations_df.loc[:,all_contexts]
    results_dict = {}
    i = -1000
    for mut_index, mut_row in new_mut_df.iterrows():
        results_dict[i] = [(sum(mut_row.tolist()))]
        i += 1
    result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])
    result_df_normalized = result_df.divide(result_df.median())
    return result_df_normalized

def df_just_raw_counts(mutation_counts: Path, iupac: str):
    mutations_df = pd.read_csv(mutation_counts, sep= '\t', index_col=0, header=0)
    contexts = Tools.contexts_in_iupac(iupac)
    all_contexts = contexts
    for item in contexts:
        rev_comp = Tools.reverse_complement(item)
        if rev_comp not in all_contexts:
            all_contexts.append(rev_comp)
    new_mut_df = mutations_df.loc[:,all_contexts]
    results_dict = {}
    i = -1000
    for mut_index, mut_row in new_mut_df.iterrows():
        results_dict[i] = [(sum(mut_row.tolist()))]
        i += 1
    result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])
    return result_df


# counts all the different positions in the dyad file
import multiprocessing as mp
import Statistics
from pathlib import Path

if __name__ == '__main__':
    mp.freeze_support()
    fasta_counter = Statistics.MutationIntersector(
        mutation_file = Path('/media/cam/Data9/CortezAnalysis/Cam_calls/8-oxo-G_Mapping_Data/split-reads/joined_bed/SRR_69-70_adjusted_filtered_sorted.bed'),
        # mutation_file = Path('/media/cam/Data9/CortezAnalysis/Cam_calls/Analysis/vcf_files/concat/KM_treated_filtered_sorted.bed'),
        dyad_file = Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_filtered_sorted.bed')
    )
