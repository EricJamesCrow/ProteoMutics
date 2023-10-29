from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data_handlers import process_files
from app.logic import mutation_intersector

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

class RunAnalysisRequest(BaseModel):
    mutation_file_path: str
    nucleosome_file_path: str
    fasta_file_path: str

router = APIRouter()

def pre_process_mutation(mutation_file_path, fasta_file_path):
    logging.info('[Mutation] Checking if pre-processing is needed')
    mutation_file = process_files.MutationFile(filepath=mutation_file_path, fasta=fasta_file_path)
    mutation_file.pre_process()
    
    return mutation_file.mut

def pre_process_nucleosome(nucleosome_file_path, fasta_file_path):
    logging.info('[Nucleosome] Checking if pre-processing is needed')
    nucleosome_file = process_files.DyadFile(filepath=nucleosome_file_path, fasta=fasta_file_path)
    nucleosome_file.pre_process()

    return nucleosome_file.nuc

def pre_process_fasta(fasta_file_path):
    logging.info('[Fasta] Checking if pre-processing is needed')
    fasta_file = process_files.FastaFile(filepath=fasta_file_path)
    fasta_file.pre_process()

    return fasta_file.filepath

@router.post("/run_analysis")
async def run_analysis(request: RunAnalysisRequest):
    mutation_file_path = Path(request.mutation_file_path)
    nucleosome_file_path = Path(request.nucleosome_file_path)
    fasta_file_path = Path(request.fasta_file_path)

    if not mutation_file_path.is_file():
        raise HTTPException(status_code=400, detail="Mutation file not found.")
    if not nucleosome_file_path.is_file():
        raise HTTPException(status_code=400, detail="Nucleosome file not found.")
    if not fasta_file_path.is_file():
        raise HTTPException(status_code=400, detail="Fasta file not found.")
    
    mutation_file_path = pre_process_mutation(mutation_file_path, fasta_file_path)
    nucleosome_file_path = pre_process_nucleosome(nucleosome_file_path, fasta_file_path)
    fasta_file_path = pre_process_fasta(fasta_file_path)
    
    print('[Intersector] Beginning intersection')
    results_file = mutation_intersector.MutationIntersector(mutation_file=mutation_file_path, dyad_file=nucleosome_file_path).run()
    print('[Intersector] Intersection complete, file saved to:', results_file)
    return {"result_file": results_file}