from django.http import JsonResponse
import python.Controller as Controller
import python.DataFrameOperations as DataFrameOperations
import python.Graphing as Graphing
import python.MutationIntersector as MutationIntersector
from pathlib import Path
import json

def check_preprocessed_files(request):
    if request.method == 'POST':
        data = json.loads(request.body) # Parse stringified JSON data
        file_path = data.get('file_path')
        file_path = Path(file_path)
        file_type = data.get('type')
        is_preprocessed = Controller.check_if_pre_processed(file_path=file_path, typ=file_type)
        return JsonResponse({'is_preprocessed': is_preprocessed})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def run_analysis(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')) # Parse stringified JSON data
        mutation_file_path = data.get('mutation_file_path')
        mutation_file_path = Path(mutation_file_path)
        nucleosome_file_path = data.get('nucleosome_file_path')
        nucleosome_file_path = Path(nucleosome_file_path)
        fasta_file_path = data.get('fasta_file_path')
        fasta_file_path = Path(fasta_file_path)
        if not Controller.check_if_pre_processed(file_path=mutation_file_path, typ='mutation'):
            mutation_file_path = Controller.pre_process_mutation_file(file_path=mutation_file_path, fasta_file=fasta_file_path)
        if not Controller.check_if_pre_processed(file_path=nucleosome_file_path, typ='nucleosome'):
            nucleosome_file_path = Controller.pre_process_nucleosome_map(file_path=nucleosome_file_path, fasta_file=fasta_file_path)
        if not Controller.check_if_pre_processed(file_path=fasta_file_path, typ='fasta'):
            fasta_file_path = Controller.pre_process_fasta(file_path=fasta_file_path)
        results_file = MutationIntersector(mutation_file_path=mutation_file_path, nucleosome_file_path=nucleosome_file_path)
        return results_file

    
def plot_graph_data(request):
    if request.method == 'POST':
        data = json.loads(request.body) # Parse stringified JSON data
        mutation_file_path = data.get('mutation_file_path')
        mutation_file_path = Path(mutation_file_path)
        # nucleosome_file_path = data.get('nucleosome_file_path')
        # nucleosome_file_path = Path(nucleosome_file_path)
        df = DataFrameOperations.format_dataframe(mutation_counts=mutation_file_path, iupac='NNN', count_complements=False, normalize_to_median=True, z_score_filter=None)
        graph_object, period, confidence, signal_to_noise = Graphing.display_figure(Graphing.make_graph(df))
        return JsonResponse({"graph_html": graph_object,
                             "period": period,
                             "confidence": confidence,
                             "signal_to_noise": signal_to_noise})
    else:
        return JsonResponse({'error': 'Invalid request method'})