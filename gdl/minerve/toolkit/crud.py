import hashlib

from django.http import JsonResponse

from minerve.toolkit.serialisers import edit_row_serialiser


def crud_update_record_json(record,fields,readonly_fields,post_url):
    data,hex = edit_row_serialiser(record,fields,readonly_fields)

    retr = {
        "res":"ok",
        "type":"record_update",
        "post_url":post_url,
        "sha512": hex,
        "fields":data,
    }
    if hasattr(record,"uuid"):
        retr["uuid"] = str(record.uuid)
    return JsonResponse(retr,safe=False)