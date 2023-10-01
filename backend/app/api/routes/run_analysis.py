from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data_handlers import controller
from app.logic import mutation_intersector

from pathlib import Path

class RunAnalysisRequest(BaseModel):
    mutation_file_path: str
    nucleosome_file_path: str
    fasta_file_path: str

router = APIRouter()

@router.post("/run_analysis")
async def run_analysis(request: RunAnalysisRequest):
    try:
        mutation_file_path = Path(request.mutation_file_path)
        nucleosome_file_path = Path(request.nucleosome_file_path)
        fasta_file_path = Path(request.fasta_file_path)
        
        print('[Mutation]Checking if pre-processing is needed')
        if mutation_file_path.suffix != '.mut':
            if controller.check_if_pre_processed(file_path=mutation_file_path, typ='mutation'):
                directory = mutation_file_path.parent
                nucleomutics_folder = directory.joinpath(mutation_file_path.with_name(mutation_file_path.stem+'_nucleomutics').stem)
                mutation_file_path = nucleomutics_folder.joinpath(mutation_file_path.with_suffix('.mut').name)
            else:
                mutation_file_path = controller.pre_process_mutation_file(file_path=mutation_file_path, fasta_file=fasta_file_path)
        
        print('[Nucleosome]Checking if pre-processing is needed')
        if not (nucleosome_file_path.suffix == '.nuc' and nucleosome_file_path.with_suffix('.counts').exists()):
            if controller.check_if_pre_processed(file_path=nucleosome_file_path, typ='nucleosome'):
                directory = nucleosome_file_path.parent
                nucleomutics_folder = directory.joinpath(nucleosome_file_path.with_name(nucleosome_file_path.stem+'_nucleomutics').stem)
                nucleosome_file_path = nucleomutics_folder.joinpath(nucleosome_file_path.with_suffix('.nuc').name)
            else:
                nucleosome_file_path = controller.pre_process_nucleosome_map(file_path=nucleosome_file_path, fasta_file=fasta_file_path)[0]
        
        print('[Fasta]Checking if pre-processing is needed')
        if not controller.check_if_pre_processed(file_path=fasta_file_path, typ='fasta'):
            fasta_file_path = controller.pre_process_fasta(fasta_file=fasta_file_path)
        
        print('###################################################################\nRUNNING INTERSRCTOR\n###################################################################')
        results_file = mutation_intersector.MutationIntersector(mutation_file=mutation_file_path, dyad_file=nucleosome_file_path).run()
        print('Done')
        return {"result_file": results_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {e}")