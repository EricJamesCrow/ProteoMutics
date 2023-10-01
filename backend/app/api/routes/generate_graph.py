from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils import DataFrameOperations, Graphing

from pathlib import Path

class PlotGraphDataRequest(BaseModel):
    mutation_file_path: str

router = APIRouter()

@router.post("/generate_graph")
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