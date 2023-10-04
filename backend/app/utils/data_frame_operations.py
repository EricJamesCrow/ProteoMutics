from . import tools

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
# from . import Tools
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
    def genome_wide_normalization(mutations_df: pd.DataFrame, dyads_df: pd.DataFrame, genome_df: pd.DataFrame, observed_df: pd.DataFrame):
        total_genome = genome_df['COUNTS'].sum()
        contexts = tools.contexts_in_iupac('NNN')

        # Calculate the expected values
        mut_counts = mutations_df.loc[contexts, 'COUNTS']
        genome_counts = genome_df.loc[contexts, 'COUNTS']

        expected_matrix = dyads_df[contexts].mul(mut_counts * (genome_counts / total_genome))
        expected_values = expected_matrix.sum(axis=1)

        # Calculate normalized values
        observed_sums = observed_df.sum(axis=1)
        fold_changes = np.log2(observed_sums.div(expected_values))
        print('hi')
        return fold_changes.to_frame(name='fold_change')

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
