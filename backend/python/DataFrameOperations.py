import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from . import Tools

def format_dataframe(mutation_counts: Path, dyad_counts: 'Path | None' = None, iupac = 'NNN', count_complements = False, normalize_to_median = True, z_score_filter: None | float = None) -> pd.DataFrame:
    """Takes a `Path` object to a saved DataFrame and counts across rows to get 2-D x and y data points to graph.
    Takes a `Path` object to a saved DataFrame with dyad position counts to normalize to if desired, as well as filters out certian contexts mutations occur in to stratify
    the data. It can count reverse complements of the IUPAC notation. Lastly it will normalize to a median value for each column
    if you want to scale the median to 1.

    Args:
    -----
        mutation_counts (Path): Path(path/to/counts/DataFrame/saved_file.txt)
        dyad_counts (Path, optional): Path(path/to/DYAD/counts.txt). Defaults to None.
        iupac (str, optional): IUPAC notation of which contexts you want to KEEP in the output. Defaults to 'NNN'.
        count_complements (bool, optional): If you would like to count reverse complements of whichever context you input. Defaults to False.
        normalize_to_median (bool, optional): If `True`, normalizes final results to the median. Defaults to True.
        z_score_filter (int, optional): If you want to filter data points based on the z_score and standard deviation, defaults to None.

    Returns:
    --------
        pd.DataFrame: pandas DataFrame in 2-D structure that can be graphed.
    """

    # creates a list of trinucleotide contexts that the IUPAC notation covers
    contexts = Tools.contexts_in_iupac(iupac)

    # if counting reverse complements, adds the reverse complements and combines them into one large sorted list to match contexts
    if count_complements:
        
        # gets the contexts in the reverse complement of the IUPAC notation
        reverse_complement_contexts = Tools.contexts_in_iupac(Tools.reverse_complement(iupac))
        # merges the sets together so it keeps unique contexts
        all_contexts = set(reverse_complement_contexts).union(set(contexts))
        # puts them into a sorted list to match the format of contexts (not necessary)
        all_contexts = sorted(list(all_contexts))
    
    # otherwise keeps just assigns all_contexts the contexts list 
    else:
        all_contexts = contexts    

    # 
    results_dict = {}
    i = -1000
    mutations_df = pd.read_csv(mutation_counts, sep= '\t', index_col=0, header=0)
    new_mut_df = mutations_df.loc[:,all_contexts]
    if dyad_counts:
        dyads_df = pd.read_csv(dyad_counts, sep= '\t', index_col=0, header=0)
        new_dyad_df = dyads_df.loc[:,all_contexts]
        for mut_index, mut_row in new_mut_df.iterrows():
            results_dict[i] = [(sum(mut_row.tolist())/sum(new_dyad_df.loc[mut_index].tolist()))]
            i += 1
    else:
        for _, mut_row in new_mut_df.iterrows():
            results_dict[i] = [(sum(mut_row.tolist()))]
            i += 1
    result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])
    if z_score_filter:
        result_df = result_df[(np.abs(stats.zscore(result_df)) < z_score_filter).all(axis=1)]
    if normalize_to_median:
        result_df_normalized = result_df.divide(result_df.median())
        return result_df_normalized
    else:
        return result_df
