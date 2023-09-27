set up and run the sever
```
fix this
Internal Server Error: /api/run_analysis
Traceback (most recent call last):
  File "/home/cam/.local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 56, in inner
    response = get_response(request)
  File "/home/cam/.local/lib/python3.10/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/cam/Documents/repos/ProteoMutics/backend/server/views.py", line 48, in run_analysis
    results_file = MutationIntersector.MutationIntersector(mutation_file=mutation_file_path, dyad_file=nucleosome_file_path, output_file=mutation_file_path.with_name(mutation_file_path.stem + '_' + nucleosome_file_path.stem + '.intersect'))
AttributeError: 'NoneType' object has no attribute 'stem'
[15/Nov/2021 16:39:00] "POST /api/run_analysis HTTP/1.1" 500 105954
```


period = 207
first peak = 0
0-74 bp per half of a nucleosome
133-207 bp per first half of a nucleosome
207 -281 bp per second half of a nucleosome