import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from math import log2
import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')
from app.utils import tools

class DataFormatter:
    @staticmethod
    def read_dataframe(file_path: str | Path, columns: list = None) -> pd.DataFrame:
        file_path = Path(file_path)
        df = pd.read_csv(file_path, sep='\t', index_col=0, header=0)
        if columns:
            df = df.loc[:, columns]
        return df

    @staticmethod
    def calculate_percentages(row):
        row_sum = row.sum()
        return [entry/row_sum for entry in row]

    @staticmethod
    def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        return df.divide(df.median())
    
    @staticmethod
    def reverse_complement_strand_conversion(df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        
        # Convert column headers to their reverse complement
        df_copy.columns = [tools.reverse_complement(col) for col in df_copy.columns]
        
        # Ensure that the columns in df_copy match the original order in df
        df_copy = df_copy[df.columns]

        # Add the two DataFrames together
        result_df = df.add(df_copy)

        return result_df

    @staticmethod
    def reverse_complement_positional_strand_conversion(df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()

        # Convert column headers to their reverse complement
        df_copy.columns = [tools.reverse_complement(col) for col in df_copy.columns]

        # Ensure that the columns in df_copy match the original order in df
        df_copy = df_copy[df.columns]

        # Reverse the order of the rows in df_copy and adjust indices
        df_copy = df_copy.iloc[::-1].set_index(-df_copy.index)

        # Reorder rows of df_copy to match the original df
        df_copy = df_copy.reindex(df.index)

        result_df = df.add(df_copy)

        return result_df
    
    @staticmethod
    def reverse_complement_tri_counts(df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        
        # Convert indices to their reverse complement
        df_copy.index = [tools.reverse_complement(idx) for idx in df_copy.index]
        
        # Ensure that the indices in df_copy match the original order in df
        df_copy = df_copy.reindex(df.index)

        # Add the two DataFrames together
        result_df = df.add(df_copy)

        return result_df

    @staticmethod
    def filter_by_z_score(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
        return df[(np.abs(stats.zscore(df)) < threshold).all(axis=1)]

    @staticmethod
    def get_all_contexts(contexts, iupac, count_complements):
        if count_complements:
            reverse_complement_contexts = tools.contexts_in_iupac(tools.reverse_complement(iupac))
            all_contexts = sorted(list(set(reverse_complement_contexts).union(set(contexts))))
        else:
            all_contexts = contexts
        return all_contexts

    @staticmethod
    def aggregate_counts(dataframe):
        """
        Aggregates counts by context from the provided dataframe.

        Args:
        dataframe (pd.DataFrame): A dataframe containing mutation contexts and their counts.

        Returns:
        pd.DataFrame: A dataframe with the total counts for each context.
        """
        # Check if the dataframe is empty (retain this check as it's important)
        if dataframe.empty:
            raise ValueError("Input DataFrame is empty.")

        # No need to check for the 'Position' column because we're aggregating values,
        # and 'Position' is not used here. This is assuming 'Position' is an index or not relevant
        # for the sum operation.

        # The actual aggregation operation: summing across rows (for each column) as you are 
        # dealing with counts across different contexts (columns).
        total_counts = dataframe.sum(axis=0)  # axis=0 is default and can be omitted, added here for clarity.

        # Transposing the result, so the output is a DataFrame with contexts as the index 
        # and a single column 'COUNTS' containing the sums. This is more a reshaping than a 
        # transposition in the traditional sense, as we're not swapping rows and columns but 
        # rather converting a Series to a DataFrame.
        df_aggregated = total_counts.to_frame(name='COUNTS')

        # If you want 'COUNTS' to be your index, you can uncomment the following line. 
        # This will transpose the DataFrame, making the single row of totals into a single 
        # column of totals with the index being 'COUNTS'.
        # df_aggregated = df_aggregated.T  # Uncomment if 'COUNTS' should be the index.

        # Returning the resulting dataframe
        return df_aggregated


    @staticmethod
    def genome_wide_normalization(mutations_df: pd.DataFrame, dyads_df: pd.DataFrame, genome_df: pd.DataFrame, observed_df: pd.DataFrame) -> pd.DataFrame:

        # Ensure input DataFrames are not empty
        for df, name in zip([mutations_df, dyads_df, genome_df, observed_df], ['mutations_df', 'dyads_df', 'genome_df', 'observed_df']):
            if df.empty:
                raise ValueError(f"The provided {name} is empty.")

        # aggregate_mutations_df = DataFormatter.aggregate_counts(observed_df)
        # frequency = aggregate_mutations_df.div(genome_df, axis=1).T
        frequency = mutations_df.div(genome_df, axis=1).T
        expected_df = dyads_df.mul(frequency.squeeze(), axis=1)

        graphing_data = (observed_df.sum(axis=1) / expected_df.sum(axis=1)).to_frame(name='normalized_column')  # You can name 'result_column' to whatever column name you desire   

        return graphing_data

    @staticmethod
    def context_normalization(mutations_df, dyads_df):
        results_dict = {}
        for mut_position, mut_row in mutations_df.iterrows():
            results_dict[mut_position] = sum(mut_row.tolist()) / sum(dyads_df.loc[mut_position].tolist())
        return pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])

    @staticmethod
    def process_without_dyad_counts(mutations_df):
        results_dict = {}
        for mut_position, mut_row in mutations_df.iterrows():
            results_dict[mut_position] = sum(mut_row.tolist())
        return results_dict

    @staticmethod
    def format_dataframe(mutation_counts: str | Path, dyad_counts: 'Path | None' = None, iupac = 'NNN', context_normalize = False, count_complements = False, normalize_to_median = True, z_score_filter: float = None) -> pd.DataFrame:
        mutation_counts = Path(mutation_counts)
        dyad_counts = Path(dyad_counts) if dyad_counts else None
        contexts = tools.contexts_in_iupac(iupac)
        all_contexts = DataFormatter.get_all_contexts(contexts, iupac, count_complements)

        if dyad_counts and not context_normalize:
            mutations_df = DataFormatter.read_dataframe(mutation_counts, all_contexts)
            dyads_df = DataFormatter.read_dataframe(dyad_counts, all_contexts)
            results_dict = DataFormatter.genome_wide_normalization(mutations_df, dyads_df)

        elif dyad_counts and context_normalize:
            mutations_df = DataFormatter.read_dataframe(mutation_counts, all_contexts)
            dyads_df = DataFormatter.read_dataframe(dyad_counts, all_contexts)
            results_dict = DataFormatter.context_normalization(mutations_df, dyads_df)

        else:
            mutations_df = DataFormatter.read_dataframe(mutation_counts, all_contexts)
            results_dict = DataFormatter.process_without_dyad_counts(mutations_df)

        result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])

        if z_score_filter:
            result_df = DataFormatter.filter_by_z_score(result_df, z_score_filter)

        if normalize_to_median:
            result_df = DataFormatter.normalize_dataframe(result_df)

        return result_df
