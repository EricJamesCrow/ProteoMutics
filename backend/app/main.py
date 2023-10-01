# FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# python
from pathlib import Path

# modules
import data_handlers.Controller as Controller
import utils.DataFrameOperations as DataFrameOperations
import utils.Graphing as Graphing
import logic.MutationIntersector as MutationIntersector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class CheckPreprocessedFilesRequest(BaseModel):
    file_path: str
    type: str

@app.post("/api/check")
async def check_preprocessed_files(request: CheckPreprocessedFilesRequest):
    file_path = request.file_path
    file_type = request.type
    is_preprocessed = Controller.check_if_pre_processed(file_path=file_path, typ=file_type)
    return {'is_preprocessed': is_preprocessed}

class RunAnalysisRequest(BaseModel):
    mutation_file_path: str
    nucleosome_file_path: str
    fasta_file_path: str

@app.post("/run_analysis")
async def run_analysis(request: RunAnalysisRequest):
    mutation_file_path = Path(request.mutation_file_path)
    nucleosome_file_path = Path(request.nucleosome_file_path)
    fasta_file_path = Path(request.fasta_file_path)
    
    print('[Mutation]Checking if pre-processing is needed')
    if mutation_file_path.suffix != '.mut':
        if Controller.check_if_pre_processed(file_path=mutation_file_path, typ='mutation'):
            directory = mutation_file_path.parent
            nucleomutics_folder = directory.joinpath(mutation_file_path.with_name(mutation_file_path.stem+'_nucleomutics').stem)
            mutation_file_path = nucleomutics_folder.joinpath(mutation_file_path.with_suffix('.mut').name)
        else:
            mutation_file_path = Controller.pre_process_mutation_file(file_path=mutation_file_path, fasta_file=fasta_file_path)
    
    print('[Nucleosome]Checking if pre-processing is needed')
    if not (nucleosome_file_path.suffix == '.nuc' and nucleosome_file_path.with_suffix('.counts').exists()):
        if Controller.check_if_pre_processed(file_path=nucleosome_file_path, typ='nucleosome'):
            directory = nucleosome_file_path.parent
            nucleomutics_folder = directory.joinpath(nucleosome_file_path.with_name(nucleosome_file_path.stem+'_nucleomutics').stem)
            nucleosome_file_path = nucleomutics_folder.joinpath(nucleosome_file_path.with_suffix('.nuc').name)
        else:
            nucleosome_file_path = Controller.pre_process_nucleosome_map(file_path=nucleosome_file_path, fasta_file=fasta_file_path)[0]
    
    print('[Fasta]Checking if pre-processing is needed')
    if not Controller.check_if_pre_processed(file_path=fasta_file_path, typ='fasta'):
        fasta_file_path = Controller.pre_process_fasta(fasta_file=fasta_file_path)
    
    print('###################################################################\nRUNNING INTERSRCTOR\n###################################################################')
    try:
        results_file = MutationIntersector.MutationIntersector(mutation_file=mutation_file_path, dyad_file=nucleosome_file_path).run()
        print('Done')
        return {"result_file": results_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {e}")

class PlotGraphDataRequest(BaseModel):
    mutation_file_path: str

@app.post("/generate_graph")
async def plot_graph_data(request: PlotGraphDataRequest):
    mutation_file_path = Path(request.mutation_file_path)

    df = DataFrameOperations.format_dataframe(
        mutation_counts=mutation_file_path, 
        iupac='NNN', 
        count_complements=False, 
        normalize_to_median=True, 
        z_score_filter=None
    )
    try:
        graph_object, period, confidence, signal_to_noise = Graphing.display_figure(Graphing.make_graph(df))
        return {
            "graph_html": graph_object,
            "period": period,
            "confidence": confidence,
            "signal_to_noise": signal_to_noise
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {e}")

@app.get("/")
async def root():
    return {"message": "Hello World"}