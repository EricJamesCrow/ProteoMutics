from django.http import JsonResponse
import python.Controller as Controller

def check_preprocessed_files(request):
    print("triggered")
    request["Access-Control-Allow-Origin"] = "http://localhost:3000"
    request["Access-Control-Allow-Methods"] = "POST"
    request["Access-Control-Allow-Headers"] = "http://localhost:3000"
    file_path = request.POST.get('file_path')
    file_type = request.POST.get('type')
    print(file_path)
    print(file_type)
    if request.method == 'POST':
        is_preprocessed = Controller.check_if_pre_processed(file_path=file_path, typ=file_type)
        print(is_preprocessed)
        return JsonResponse({'is_preprocessed': is_preprocessed})