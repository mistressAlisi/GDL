from django.forms import model_to_dict
from django.http import JsonResponse

from minerve.toolkit.serialisers import filtered_serialiser, filtered_serialiser_many, model_metadata


def paginator_json_response(_obj,page_size=20,form_values={}):
    """
    Generate a Paginator JSON response for metadata from the given _obj.
    @param _obj: Object iterator
    @type _obj: Any Object/QuerySet.
    @return: JSONResponse
    @rtype: JSONResponse
    """
    _,_,cols = model_metadata(_obj[0])
    return JsonResponse({"res": "ok", "paginator": {"total_pages": round(_obj.count() / page_size), "current_page": 1, "total_records": _obj.count()},"columns":cols,"values":{"data":form_values}})


def paginator_paginate_object(_obj,page=1,page_size=20):
    """
    Paginate a QuerySet _obj for paginator views
    @param _obj: Object iterator
    @type _obj: Any Object/QuerySet.
    @param page: Page Number to display, default 1.
    @type page: int
    @return: pobjs,start,end,page,total_records,total_pages,paginator_range
    @rtype: Paginated Queryset,Start Record, End Record, Page Count, Total Records, Total Pages, Paginator Range
    """
    try:
        total_records =  _obj.count()
    except TypeError:
        total_records = len(_obj)
    total_pages = round(total_records / page_size)
    if total_pages >= 2:
        paginator_range = list(range(1, total_pages + 1))
    else:
        paginator_range = [1]
    if hasattr(_obj,"created"):
        objs = _obj.order_by("created")
    else:
        objs = _obj
    if page > 1:
        start = (page-1)*page_size
    else:
        start = 0
    end = start + page_size
    pobjs = objs[start:end]
    # print(objs,pobjs,start,end,page,total_records,total_pages,paginator_range)
    return pobjs,start,end,page,total_records,total_pages,paginator_range


def paginator_paginate_and_serialise(_obj,page=1,page_size=20,filter_cols=[],relation_names={},**kwargs):
    """
    Leverage the Paginator and Simple serialisers to create a one-liner interface suitable for use with AJAX/JSON requests,
    such as with the TableApp SDK shipping with Minerve.
    :param _obj: QuerySet of objects to paginate
    :param page: Current page, default is 1.
    :param page_size: Page size, default is 20
    :param filter_cols: Filter columns array, default is none. - if specified, only return these cols.
    :return: JSONResponse object containing paginator_table data.
    """
    if len(_obj) == 0:
        return JsonResponse({"res":"ok","type":"paginator_table","data": {"empty":True,"paginator":{"current_page":1}}})
    annotations = {}
    if hasattr(_obj, "query"):
        annotations = _obj.query.annotations or {}
    pobjs,start,end,page,total_records,total_pages,paginator_range = paginator_paginate_object(_obj,page,page_size)
    # print(pobjs)
    # print("Right before FSM")
    if "set_columns" in kwargs:
        set_columns = kwargs["set_columns"]
    else:
        set_columns = False
    spobjs,vnames,htext = filtered_serialiser_many(pobjs,filter_cols,relation_names,annotations=annotations,set_columns=set_columns)
    if "additional_col_names" in kwargs:
        vnames.update(kwargs["additional_col_names"])
    _,_,cols = model_metadata(_obj[0])
    # print(vnames)
    retrObj =  {
        "paginator": {"total_pages": round(_obj.count() / page_size), "current_page": page, "total_records": _obj.count()},
        "total_records":total_records,
        "total_pages":total_pages,
        "column_names":vnames,
        "columns": cols,
        "help_text":htext,
        "start":start,
        "end":end,
        "rows":spobjs,
        "filter_cols": filter_cols,
        }
    if "additional_cols" in kwargs:
        retrObj["additional_cols"] = kwargs["additional_cols"]
    if "totals" in kwargs:
        retrObj["totals"] = kwargs["totals"]
    return JsonResponse({"res":"ok","type":"paginator_table","data":retrObj})
