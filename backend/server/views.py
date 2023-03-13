from django.http import JsonResponse
import python.Controller as Controller
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