from django.http import JsonResponse

# def drink_list(request):
#     if request.method == 'GET':
#         drinks = Drink.objects.all()
#         serializer = DrinkSerializer(drinks, many=True)
#         return JsonResponse(serializer.data, safe=False)

#     elif request.method == 'POST':
#         data = JSONParser().parse(request)
#         serializer = DrinkSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)