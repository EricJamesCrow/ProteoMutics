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
        file_type = data.get('type')
        is_preprocessed = Controller.check_if_pre_processed(file_path=file_path, typ=file_type)
        return JsonResponse({'is_preprocessed': is_preprocessed})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def run_analysis(request):
    print('run_analysis')
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')) # Parse stringified JSON data
        mutation_file_path = data.get('mutation_file_path')
        mutation_file_path = Path(mutation_file_path)
        nucleosome_file_path = data.get('nucleosome_file_path')
        nucleosome_file_path = Path(nucleosome_file_path)
        fasta_file_path = data.get('fasta_file_path')
        fasta_file_path = Path(fasta_file_path)
        print('[Mutation]Checking if pre-processing is needed')
        if mutation_file_path.suffix == '.mut':
            pass
        else:
            if Controller.check_if_pre_processed(file_path=mutation_file_path, typ='mutation'):
                directory = mutation_file_path.parent
                nucleomutics_folder = directory.joinpath(mutation_file_path.with_name(mutation_file_path.stem+'_nucleomutics').stem)
                mutation_file_path = nucleomutics_folder.joinpath(mutation_file_path.with_suffix('.mut').name)
            else:
                mutation_file_path = Controller.pre_process_mutation_file(file_path=mutation_file_path, fasta_file=fasta_file_path)
        print('[Nucleosome]Checking if pre-processing is needed')
        if nucleosome_file_path.suffix == '.nuc' and nucleosome_file_path.with_suffix('.counts').exists():
            pass
        else:
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
        results_file = MutationIntersector.MutationIntersector(mutation_file=mutation_file_path, dyad_file=nucleosome_file_path).run()
        print('Done')
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