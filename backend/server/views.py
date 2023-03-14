from django.http import JsonResponse
import python.Controller as Controller
import python.DataFrameOperations as DataFrameOperations
import python.Graphing as Graphing
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
    
def plot_graph_data(request):
    if request.method == 'POST':
        data = json.loads(request.body) # Parse stringified JSON data
        mutation_file_path = data.get('mutation_file_path')
        mutation_file_path = Path(mutation_file_path)
        # nucleosome_file_path = data.get('nucleosome_file_path')
        # nucleosome_file_path = Path(nucleosome_file_path)
        df = DataFrameOperations.format_dataframe(mutation_counts=mutation_file_path, iupac='NNN', count_complements=False, normalize_to_median=True, z_score_filter=None)
        Graphing.make_graph(df)
        # return JsonResponse({'graph_data': graph_data})
    else:
        return JsonResponse({'error': 'Invalid request method'})