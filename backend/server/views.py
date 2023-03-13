from django.http import JsonResponse
import python.Controller as Controller

def check_preprocessed_files(request):
    print("triggered")
    file_path = request.POST.get('file_path')
    file_type = request.POST.get('type')
    if request.method == 'POST':
        is_preprocessed = Controller.check_if_pre_processed(file_path=file_path, typ=file_type)
        print(is_preprocessed)
        return JsonResponse({'is_preprocessed': is_preprocessed})