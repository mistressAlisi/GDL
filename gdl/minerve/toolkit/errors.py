from django.http import JsonResponse


def generic_json_error(errstr="Error!",errdata={}):
    return JsonResponse({"res": "err", "err": errstr, "data": errdata})
