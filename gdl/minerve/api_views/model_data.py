import importlib

from aiohttp.web_response import json_response
from django.contrib.auth.decorators import login_required


@login_required
def get_model_data_handle(request,model_name):
    model_path = model_name.split('.')
    models = importlib.import_module(f"{model_path[0]}.models"
                                     f".{model_path[1]}")
    print(models)
    return json_response("ok")