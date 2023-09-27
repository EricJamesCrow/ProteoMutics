import numpy as np  # Importing numpy for handling numerical computations
import pandas as pd  # Importing pandas for handling structured data
from scipy import stats  # Importing stats module from scipy for statistical functions
from pathlib import Path  # Importing Path from pathlib for dealing with paths
# from . import Tools  # Importing Tools module from the current package
import Tools

# Defining the function format_dataframe
def format_dataframe(mutation_counts: Path, dyad_counts: 'Path | None' = None, iupac = 'NNN', normalize_to_tri = False, count_complements = False, normalize_to_median = True, z_score_filter: float = None) -> pd.DataFrame:
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
    # Creating a list of trinucleotide contexts according to the IUPAC notation
    contexts = Tools.contexts_in_iupac(iupac)

    # Checking if the count_complements flag is set
    if count_complements:
        # Getting the reverse complements of the IUPAC notation contexts
        reverse_complement_contexts = Tools.contexts_in_iupac(Tools.reverse_complement(iupac))
        # Merging both sets of contexts into one while keeping unique contexts
        all_contexts = set(reverse_complement_contexts).union(set(contexts))
        # Converting the set of all_contexts into a sorted list
        all_contexts = sorted(list(all_contexts))
    else:
        # If the count_complements flag is not set, assign the original contexts to all_contexts
        all_contexts = contexts   

    # Initializing an empty dictionary to store results
    results_dict = {}
    i = -1000
    # Reading a dataframe from the mutation_counts file
    mutations_df = pd.read_csv(mutation_counts, sep= '\t', index_col=0, header=0)
    # Selecting columns from the dataframe that match the all_contexts list
    new_mut_df = mutations_df.loc[:,all_contexts]
    # Checking if a dyad_counts file was provided
    if dyad_counts and not normalize_to_tri:
        # Reading a dataframe from the dyad_counts file
        dyads_df = pd.read_csv(dyad_counts, sep= '\t', index_col=0, header=0)
        # Selecting columns from the dyad dataframe that match the all_contexts list
        new_dyad_df = dyads_df.loc[:,all_contexts]
        # Looping over each row in the mutations dataframe
        for mut_position, mut_row in new_mut_df.iterrows():
            expected_values = []
            # Computing the sum of the row divided by the sum to get a percentage
            mut_row_sum = mut_row.sum()
            mut_row_percentages = [entry/mut_row_sum for entry in mut_row]
            # print(mut_row_percentages)
            # Computing the sum of the corresponding dyad row and divide by that to get a percentage
            dyad_row_sum = new_dyad_df.loc[mut_position].sum()
            dyad_percentage_list = [entry/dyad_row_sum for entry in new_dyad_df.loc[mut_position]]
            # print(dyad_percentage_list)
            # Multiply the percentages from mut_row and the dyad row, then multiply by mut_row_sum
            for mut_percentage, dyad_percentage in zip(mut_row_percentages, dyad_percentage_list):
                expected_value = mut_percentage * dyad_percentage * mut_row_sum
                expected_values.append(expected_value)
            results_dict[i] = mut_row_sum/sum(expected_values)
            i += 1
    elif dyad_counts and normalize_to_tri:
        # Reading a dataframe from the dyad_counts file
        dyads_df = pd.read_csv(dyad_counts, sep= '\t', index_col=0, header=0)
        # Selecting columns from the dyad dataframe that match the all_contexts list
        new_dyad_df = dyads_df.loc[:,all_contexts]
        for mut_position, mut_row in new_mut_df.iterrows():
            results_dict[i] = [(sum(mut_row.tolist())/sum(new_dyad_df.loc[mut_position].tolist()))]
            i += 1
    else:
        # If a dyad_counts file was not provided, loop over each row in the mutations dataframe
        for _, mut_row in new_mut_df.iterrows():
            # Computing the sum of the row
            # Storing the result in the results dictionary with a unique key
            results_dict[i] = [(sum(mut_row.tolist()))]
            i += 1
    # Creating a new dataframe from the results dictionary
    result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])
    # Checking if a z_score_filter value was provided
    if z_score_filter:
        # Filtering the dataframe to only include rows with a z-score less than the z_score_filter
        result_df = result_df[(np.abs(stats.zscore(result_df)) < z_score_filter).all(axis=1)]
    # Checking if the normalize_to_median flag is set
    if normalize_to_median:
        # Normalizing the dataframe by dividing each value by the median
        result_df_normalized = result_df.divide(result_df.median())
        return result_df_normalized
    else:
        return result_df
