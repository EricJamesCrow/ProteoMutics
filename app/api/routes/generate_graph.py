from app.utils import graphing, data_frame_operations

from pathlib import Path

def plot_graph_data(mutation_file_path: str) -> dict:
    mutation_file_path = Path(mutation_file_path)

    df = data_frame_operations.format_dataframe(
        mutation_counts=mutation_file_path, 
        iupac='NNN', 
        count_complements=False, 
        normalize_to_median=True, 
        z_score_filter=None
    )
    try:
        graph_object, period, confidence, signal_to_noise = graphing.display_figure(graphing.make_graph(df))
        # switch html to output png
        return {
            "graph_html": graph_object,
            "period": period,
            "confidence": confidence,
            "signal_to_noise": signal_to_noise
        }
    except Exception as e:
        pass