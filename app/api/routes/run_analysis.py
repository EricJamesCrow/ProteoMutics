import sys
sys.path.append('app')

#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

# Assuming these imports match your existing directory structure
from app.data_handlers import process_files
from app.logic import mutation_intersector

logging.basicConfig(level=logging.INFO)

def pre_process_mutation(mutation_file_path: Path, fasta_file_path: Path) -> Path:
    """
    Checks if mutation file preprocessing is needed, and performs it if necessary.
    Returns the path to the preprocessed mutation file.
    """
    logging.info('[Mutation] Checking if pre-processing is needed')
    mutation_file = process_files.MutationFile(filepath=mutation_file_path, fasta=fasta_file_path)
    mutation_file.pre_process()
    return mutation_file.mut

def pre_process_nucleosome(nucleosome_file_path: Path, fasta_file_path: Path) -> Path:
    """
    Checks if nucleosome file preprocessing is needed, and performs it if necessary.
    Returns the path to the preprocessed nucleosome file.
    """
    logging.info('[Nucleosome] Checking if pre-processing is needed')
    nucleosome_file = process_files.DyadFile(filepath=nucleosome_file_path, fasta=fasta_file_path)
    nucleosome_file.pre_process()
    return nucleosome_file.nuc

def pre_process_fasta(fasta_file_path: Path) -> Path:
    """
    Checks if FASTA file preprocessing is needed, and performs it if necessary.
    Returns the path to the preprocessed FASTA file.
    """
    logging.info('[Fasta] Checking if pre-processing is needed')
    fasta_file = process_files.FastaFile(filepath=fasta_file_path)
    fasta_file.pre_process()
    return fasta_file.filepath

def run_analysis(mutation_file_path: Path, nucleosome_file_path: Path, fasta_file_path: Path) -> str:
    """
    Verifies file paths exist, runs preprocessing on each file, and then runs
    the MutationIntersector logic. Returns the path to the results file.
    """
    # Validate that all provided paths exist
    if not mutation_file_path.is_file():
        raise FileNotFoundError(f"Mutation file not found at {mutation_file_path}")
    if not nucleosome_file_path.is_file():
        raise FileNotFoundError(f"Nucleosome file not found at {nucleosome_file_path}")
    if not fasta_file_path.is_file():
        raise FileNotFoundError(f"FASTA file not found at {fasta_file_path}")

    # Pre-process each file if needed
    logging.info('[Analysis] Starting file preprocessing')
    mutation_file_preprocessed = pre_process_mutation(mutation_file_path, fasta_file_path)
    nucleosome_file_preprocessed = pre_process_nucleosome(nucleosome_file_path, fasta_file_path)
    fasta_file_preprocessed = pre_process_fasta(fasta_file_path)

    # Run intersection logic
    logging.info('[Intersector] Beginning intersection')
    results_file = mutation_intersector.MutationIntersector(
        mutation_file=mutation_file_preprocessed,
        dyad_file=nucleosome_file_preprocessed
    ).run()

    logging.info('[Intersector] Intersection complete, file saved to: %s', results_file)
    return results_file

def main():
    parser = argparse.ArgumentParser(description="Run mutation-nucleosome analysis.")
    parser.add_argument(
        "--mutation_file_path",
        required=True,
        help="Path to the mutation file."
    )
    parser.add_argument(
        "--nucleosome_file_path",
        required=True,
        help="Path to the nucleosome file."
    )
    parser.add_argument(
        "--fasta_file_path",
        required=True,
        help="Path to the FASTA file."
    )

    args = parser.parse_args()

    # Convert string arguments to Path objects
    mutation_path = Path(args.mutation_file_path)
    nucleosome_path = Path(args.nucleosome_file_path)
    fasta_path = Path(args.fasta_file_path)

    # Run the analysis and print the result file
    try:
        result_file = run_analysis(mutation_path, nucleosome_path, fasta_path)
        print(f"Analysis complete. Results file: {result_file}")
    except FileNotFoundError as e:
        logging.error(e)

if __name__ == "__main__":
    main()
