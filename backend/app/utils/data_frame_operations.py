from . import tools

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
<<<<<<< HEAD:backend/utils/DataFrameOperations.py
# from . import Tools
from math import log2

import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')
from utils import Tools
=======
>>>>>>> 983731144b3d4ba6944ce45928cbac8055ccfc52:backend/app/utils/data_frame_operations.py

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
        expected = {}
        normalized = {}
        contexts = Tools.contexts_in_iupac('NNN')
        for dyad_position, dyad_row in dyads_df.iterrows():
            expected_values = []
            for context in contexts:
                try:    
                    expected_value = mutations_df.loc[context, 'COUNTS']*(genome_df.loc[context, 'COUNTS']/genome_df.sum())*(dyad_row[context]/dyad_row.sum())
                    expected_values.append(expected_value)
                except KeyError:
                    pass
            expected[dyad_position] = sum(expected_values)
        for observed_position, observed_row in observed_df.iterrows():
            normalized[observed_position] = log2(observed_row.sum()/expected[observed_position])
        return pd.DataFrame.from_dict(normalized, orient='index', columns=['fold_change'])

    @staticmethod
    def ben_genome_wide_normalization(mutations_df: pd.DataFrame, dyads_df: pd.DataFrame, genome_df: pd.DataFrame, observed_df: pd.DataFrame):
        expected = {}
        normalized = {}
        total_mutations_dict = mutations_df.to_dict()
        total_genomic_dict = genome_df.to_dict()
        contexts = Tools.contexts_in_iupac('NNN')
        for dyad_position, dyad_row in dyads_df.iterrows():
            ben_values = []
            for context in contexts:
                try:    
                    ben_value = (total_mutations_dict['COUNTS'][context]/sum(total_mutations_dict['COUNTS'].values()))*(total_genomic_dict['COUNTS'][context]/sum(total_genomic_dict['COUNTS'].values()))*(dyad_row[context])
                    ben_values.append(ben_value)
                except KeyError:
                    pass
            expected[dyad_position] = sum(ben_values)
        for observed_position, observed_row in observed_df.iterrows():
            normalized[observed_position] = observed_row.sum()/expected[observed_position]
        return pd.DataFrame.from_dict(normalized, orient='index', columns=['Counts'])
    
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
