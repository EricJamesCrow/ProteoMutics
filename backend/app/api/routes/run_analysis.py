from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data_handlers import controller
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
    if mutation_file_path.suffix != '.mut':
        if controller.check_if_pre_processed(file_path=mutation_file_path, typ='mutation'):
            directory = mutation_file_path.parent
            nucleomutics_folder = directory.joinpath(mutation_file_path.with_name(mutation_file_path.stem+'_nucleomutics').stem)
            return nucleomutics_folder.joinpath(mutation_file_path.with_suffix('.mut').name)
        else:
            return controller.pre_process_mutation_file(file_path=mutation_file_path, fasta_file=fasta_file_path)
    return mutation_file_path

def pre_process_nucleosome(nucleosome_file_path, fasta_file_path):
    logging.info('[Nucleosome] Checking if pre-processing is needed')
    if not (nucleosome_file_path.suffix == '.nuc' and nucleosome_file_path.with_suffix('.counts').exists()):
        if controller.check_if_pre_processed(file_path=nucleosome_file_path, typ='nucleosome'):
            directory = nucleosome_file_path.parent
            nucleomutics_folder = directory.joinpath(nucleosome_file_path.with_name(nucleosome_file_path.stem+'_nucleomutics').stem)
            return nucleomutics_folder.joinpath(nucleosome_file_path.with_suffix('.nuc').name)
        else:
            return controller.pre_process_nucleosome_map(file_path=nucleosome_file_path, fasta_file=fasta_file_path)[0]
    return nucleosome_file_path

def pre_process_fasta(fasta_file_path):
    logging.info('[Fasta] Checking if pre-processing is needed')
    if not controller.check_if_pre_processed(file_path=fasta_file_path, typ='fasta'):
        return controller.pre_process_fasta(fasta_file=fasta_file_path)
    return fasta_file_path

@router.post("/run_analysis")
async def run_analysis(request: RunAnalysisRequest):
    try:
        mutation_file_path = Path(request.mutation_file_path)
        nucleosome_file_path = Path(request.nucleosome_file_path)
        fasta_file_path = Path(request.fasta_file_path)

        # if not mutation_file_path.exists():
        #     raise HTTPException(status_code=400, detail="Mutation file not found.")
        # if not nucleosome_file_path.exists():
        #     raise HTTPException(status_code=400, detail="Nucleosome file not found.")
        # if not fasta_file_path.exists():
        #     raise HTTPException(status_code=400, detail="Fasta file not found.")
        
        mutation_file_path = pre_process_mutation(mutation_file_path, fasta_file_path)
        nucleosome_file_path = pre_process_nucleosome(nucleosome_file_path, fasta_file_path)
        fasta_file_path = pre_process_fasta(fasta_file_path)
        
        print('###################################################################\nRUNNING INTERSRCTOR\n###################################################################')
        results_file = mutation_intersector.MutationIntersector(mutation_file=mutation_file_path, dyad_file=nucleosome_file_path).run()
        print('Done')
        return {"result_file": results_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {e}")