import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import Tools

class DataFormatter:
    def __init__(self):
        pass

    @staticmethod
    def read_dataframe(file_path: Path, columns: list = None) -> pd.DataFrame:
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
    def filter_by_z_score(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
        return df[(np.abs(stats.zscore(df)) < threshold).all(axis=1)]

    @staticmethod
    def get_all_contexts(contexts, iupac, count_complements):
        if count_complements:
            reverse_complement_contexts = Tools.contexts_in_iupac(Tools.reverse_complement(iupac))
            all_contexts = sorted(list(set(reverse_complement_contexts).union(set(contexts))))
        else:
            all_contexts = contexts
        return all_contexts

    @staticmethod
    def process_without_context_normalization(mutations_df, dyads_df):
        results_dict = {}
        mutation_df_sum = mutations_df.values.sum()
        for mut_position, mut_row in mutations_df.iterrows():
            expected_values = []
            mut_row_percentages = DataFormatter.calculate_percentages(mut_row)
            dyad_row_percentages = DataFormatter.calculate_percentages(dyads_df.loc[mut_position])
            for mut_percentage, dyad_percentage in zip(mut_row_percentages, dyad_row_percentages):
                expected_value = mut_percentage * dyad_percentage * mutation_df_sum
                expected_values.append(expected_value)
            results_dict[mut_position] = mut_row.sum() / sum(expected_values)
        return results_dict

    @staticmethod
    def process_with_context_normalization(mutations_df, dyads_df):
        results_dict = {}
        for mut_position, mut_row in mutations_df.iterrows():
            results_dict[mut_position] = sum(mut_row.tolist()) / sum(dyads_df.loc[mut_position].tolist())
        return results_dict

    @staticmethod
    def process_without_dyad_counts(mutations_df):
        results_dict = {}
        for mut_position, mut_row in mutations_df.iterrows():
            results_dict[mut_position] = sum(mut_row.tolist())
        return results_dict

    @staticmethod
    def format_dataframe(mutation_counts: Path, dyad_counts: 'Path | None' = None, iupac = 'NNN', context_normalize = False, count_complements = False, normalize_to_median = True, z_score_filter: float = None) -> pd.DataFrame:
        contexts = Tools.contexts_in_iupac(iupac)
        all_contexts = DataFormatter.get_all_contexts(contexts, iupac, count_complements)

        if dyad_counts and not context_normalize:
            mutations_df = DataFormatter.read_dataframe(mutation_counts, all_contexts)
            dyads_df = DataFormatter.read_dataframe(dyad_counts, all_contexts)
            results_dict = DataFormatter.process_without_context_normalization(mutations_df, dyads_df)

        elif dyad_counts and context_normalize:
            mutations_df = DataFormatter.read_dataframe(mutation_counts, all_contexts)
            dyads_df = DataFormatter.read_dataframe(dyad_counts, all_contexts)
            results_dict = DataFormatter.process_with_context_normalization(mutations_df, dyads_df)

        else:
            mutations_df = DataFormatter.read_dataframe(mutation_counts, all_contexts)
            results_dict = DataFormatter.process_without_dyad_counts(mutations_df)

        result_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Counts'])

        if z_score_filter:
            result_df = DataFormatter.filter_by_z_score(result_df, z_score_filter)

        if normalize_to_median:
            result_df = DataFormatter.normalize_dataframe(result_df)

        return result_df
