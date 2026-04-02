"""
toolkit/serialisers.py
====================================
Toolkit utilities for [De]-Serialising Models.
"""
import base64
import hashlib
import importlib
import json
import mimetypes
from decimal import Decimal
from uuid import UUID

from django.db.models import ForeignKey, ManyToOneRel, CharField, FileField, ImageField
from django.db.models.fields import DateTimeField, TimeField, DateField, DecimalField, UUIDField

from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils import timezone


def _encode_filefield(file_obj, include_data: bool, max_size: int):
    """
    Safely encode a Django File/ImageField for JSON transport.
    """
    if not file_obj:
        return None

    try:
        size = file_obj.size
        name = file_obj.name
        content_type, _ = mimetypes.guess_type(name)

        payload = {
            "name": name,
            "size": size,
            "content_type": content_type or "application/octet-stream",
        }

        if include_data:
            if size > max_size:
                raise ValueError(
                    f"File too large to serialise ({size} bytes)"
                )

            file_obj.open("rb")
            try:
                raw = file_obj.read()
            finally:
                file_obj.close()

            payload.update({
                "encoding": "base64",
                "data": base64.b64encode(raw).decode("ascii"),
            })

        return payload

    except Exception as e:
        return {
            "error": str(e),
            "name": getattr(file_obj, "name", None),
        }

def model_metadata(model_instance,fields=[]):
    """
    @brief Extract Verbose name and help text from models and prepare it for serialising.
    @param model_instance: The model to parse.
    @type model_instance: Any Model Instance
    @return: verbose_names,help_text
    @rtype: dict,dict
    """
    verbose_names = {}
    help_text = {}
    types = {}
    columns = []
    for f in model_instance._meta.get_fields():
        if (type(f)) == ManyToOneRel:
            pass
        else:
            if f.name in fields or fields == []:
                columns.append(f.name)
                if hasattr(f, 'verbose_name'):
                    verbose_names[f.name] = f.verbose_name
                if hasattr(f, 'help_text'):
                    if f.help_text != "":
                        help_text[f.name] = f.help_text
    return verbose_names, help_text, columns

def simple_serialiser(model_instance,jsonify=False):
    """
    @brief SERIALISE an object and return a set of json-encodable objects suitable for AJAX/JSON requests.
    ===============================
    :param model_instance: p_model_instance: The Model instance to be serialised
    :returns: r:data, verbose_names,help_text.
    """
    verbose_names, help_text, columns = model_metadata(model_instance)
    rdata = model_to_dict(model_instance)

    for key in columns:
        # print(str(type(getattr(model_instance, key))))
        if hasattr(getattr(model_instance,key),"all"):
            rdata[key] = {"values": [], "name": key}
            for obj in getattr(model_instance,key).all():
                rdata[key]["values"].append(str(obj.pk))
        elif type(getattr(model_instance,key)) == ForeignKey:
            # print("FK")
            name =  str(model_instance)
            rdata[key] = {"value":str(rdata[key]),"name":name}
        elif(type(getattr(model_instance,key)) == UUID):
            rdata[key] = str(getattr(model_instance,key))
        else:
            rdata[key] = str(getattr(model_instance,key))
    if not jsonify:
        return rdata,verbose_names, help_text
    else:
        return JsonResponse(
            {
                "res": "ok",
                "data": rdata,
                "verbose_names": verbose_names,
                "help_text": help_text,
            }, safe=False)

def filtered_serialiser(model_instance,fields=[],jsonify=False):
    """
    @brief SERIALISE an object and return a set of json-encodable objects suitable for AJAX/JSON requests.
           based on the field names passed.
    ===============================
    :param model_instance: p_model_instance: The Model instance to be serialised
    :param List: p_fields: The list of fields to fetch and serialise.
    :returns: r:data, verbose_names,help_text.
    """
    verbose_names, help_text, columns = model_metadata(model_instance,fields)
    rdata = {}
    for key in columns:
        curr_val = getattr(model_instance, key)
        # print(curr_val)
        if model_instance._meta.get_field(key).is_relation:
            if curr_val:
                name = str(curr_val)
                rdata[key] = {"value": str(curr_val.pk), "name": name}
        elif hasattr(getattr(model_instance, key), "all"):
            rdata[key] = {"values": [], "name": key}
            for obj in getattr(model_instance, key).all():
                rdata[key]["values"].append(str(obj.pk))
        elif type(curr_val) == UUID:
            rdata[key] = str(curr_val)
        elif type(model_instance._meta.get_field(key)) == CharField:
            print(curr_val)
            rdata[key] = curr_val
            field = model_instance._meta.get_field(key)
            # print(field.choices)
            if field.choices:
                rdata[key] = getattr(model_instance, f"get_{key}_display")()
        else:
            rdata[key] = curr_val

    if not jsonify:
        return rdata,verbose_names, help_text
    else:
        return JsonResponse(
            {
                "res": "ok",
                "data": rdata,
                "verbose_names": verbose_names,
                "help_text": help_text,
            }, safe=False)


def filtered_serialiser_many(queryset, fields=None, relation_names=None,annotations=None,include_files: bool = False, max_file_size: int = 5 * 1024 * 1024, date_isoformat: bool = False,render_false_as_dash: bool = True,set_columns: list = False):
    """
    SERIALISE a queryset into JSON-encodable dicts.

    - Timezone-safe DateTime handling
    - Faster field access (no repeated meta lookups)
    - Preserves existing output structure
    - ✅ Supports annotated fields
    """
    if not queryset:
        return [], {}, {}
    if render_false_as_dash:
        nstr = "-"
    else:
        nstr = None
    fields = fields or []
    relation_names = relation_names or {}
    annotations = annotations or {}
    annotation_names = list(annotations.keys())
    model_instance = queryset[0]
    model = model_instance._meta.model

    # -------------------------
    # Base metadata (model fields)
    # -------------------------
    verbose_names, help_text, columns = model_metadata(model_instance, fields)

    # -------------------------
    # Detect annotations
    # -------------------------

    annotation_names = list(annotations.keys())

    # -------------------------
    # Extend metadata for annotations
    # -------------------------
    for name in annotation_names:
        if name not in columns:
            columns.append(name)
        verbose_names.setdefault(
            name,
            name.replace("_", " ").title(),
        )
        help_text.setdefault(name, "")

    # -------------------------
    # Field map (model fields only)
    # -------------------------

    field_map = {
        f.name: f
        for f in model._meta.get_fields()
    }

    rows = []
    if set_columns:
        columns = set_columns

        # Reorder metadata to follow set_columns
        verbose_names = {
            key: verbose_names.get(key)
            for key in columns
            if key in verbose_names
        }
        help_text = {
            key: help_text.get(key)
            for key in columns
            if key in help_text
        }

    for row in queryset:
        rdata = {}

        for key in columns:
            curr_field = field_map.get(key)
            curr_val = getattr(row, key, None)

            # --------------------
            # Annotated fields (type-aware)
            # --------------------
            if curr_field is None and key in annotation_names:
                curr_val = getattr(row, key, None)

                # DateTime annotation
                if hasattr(curr_val, "tzinfo"):
                    if curr_val:
                        local_dt = timezone.localtime(curr_val)
                        rdata[key] = (
                            local_dt.isoformat()
                            if date_isoformat
                            else local_dt.strftime("%Y-%m-%d %H:%M:%S")
                        )
                    else:
                        rdata[key] = nstr

                # Date annotation
                elif hasattr(curr_val, "year") and hasattr(curr_val, "month") and hasattr(curr_val, "day"):
                    rdata[key] = (
                        curr_val.strftime("%Y-%m-%d")
                        if curr_val else nstr
                    )

                # Time annotation
                elif hasattr(curr_val, "hour") and hasattr(curr_val, "minute"):
                    rdata[key] = (
                        curr_val.strftime("%H:%M:%S")
                        if curr_val else nstr
                    )

                # Decimal annotation
                elif isinstance(curr_val, Decimal):
                    rdata[key] = float(curr_val)

                # UUID annotation
                elif isinstance(curr_val, UUID):
                    rdata[key] = str(curr_val)

                else:
                    rdata[key] = curr_val

                continue

            # --------------------
            # Relations
            # --------------------
            if curr_field and curr_field.is_relation:
                if not curr_val:
                    rdata[key] = nstr
                    continue

                if key in relation_names:
                    attr = getattr(curr_val, relation_names[key], None)
                    name = attr() if callable(attr) else str(attr)
                else:
                    name = str(curr_val)

                if hasattr(curr_val, "all"):
                    rdata[key] = {
                        "values": [str(obj.pk) for obj in curr_val.all()],
                        "name": name,
                    }
                else:
                    rdata[key] = {
                        "value": str(curr_val.pk),
                        "name": name,
                    }
            # ───────────────
            # File / Image
            # ───────────────
            elif isinstance(curr_field, (FileField, ImageField)):
                rdata[key] = _encode_filefield(
                    curr_val,
                    include_data=include_files,
                    max_size=max_file_size,
                )
            # --------------------
            # UUID
            # --------------------
            elif isinstance(curr_val, UUID) or isinstance(curr_field,UUIDField):
                rdata[key] = str(curr_val)

            # --------------------
            # DateTime (timezone-safe)
            # --------------------
            elif isinstance(curr_field, DateTimeField):
                if curr_val:
                    if not date_isoformat:
                        local_dt = timezone.localtime(curr_val)
                        rdata[key] = local_dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        local_dt = timezone.localtime(curr_val)
                        rdata[key] = local_dt.isoformat()
                else:
                    rdata[key] = nstr

            # --------------------
            # Date
            # --------------------
            elif isinstance(curr_field, DateField):
                rdata[key] = (
                    curr_val.strftime("%Y-%m-%d")
                    if curr_val else nstr
                )

            # --------------------
            # Time
            # --------------------
            elif isinstance(curr_field, TimeField):
                rdata[key] = (
                    curr_val.strftime("%H:%M:%S")
                    if curr_val else nstr
                )
            # --------------------
            # Decimal
            # --------------------
            elif isinstance(curr_field, DecimalField):
                rdata[key] = (
                    float(curr_val)
                    if curr_val else "0"
                )

            # --------------------
            # CharField w/ choices
            # --------------------
            elif isinstance(curr_field, CharField):
                if curr_field.choices:
                    rdata[key] = getattr(row, f"get_{key}_display")()
                else:
                    rdata[key] = curr_val

            # --------------------
            # Everything else
            # --------------------
            else:
                rdata[key] = curr_val

        rdata["__pk"] = str(row.pk)
        if model._meta.pk.name == "uuid":
            rdata["uuid"] = str(row.uuid)
        rows.append(rdata)


    return rows, verbose_names, help_text




def edit_row_serialiser(model_instance,fields=False,readonly=[]):
    filter_fields = []
    chksm = ""
    retr = []
    if fields: filter_fields = fields
    for field in model_instance._meta.fields:
        if not fields:
            filter_fields.append(field.name)
        if field.name in filter_fields:
            fieldData = {"name": field.name, "verbose_name": field.verbose_name, "help_text": field.help_text,"type":field.get_internal_type()}
            if fieldData["type"] == "UUIDField":
                fieldData["type"] = "uuid"
                fieldData["value"] = str(getattr(model_instance,field.name))
            elif fieldData["type"] == "BooleanField":
                fieldData["type"] = "boolean"
                fieldData["value"] = bool(getattr(model_instance,field.name))
            elif fieldData["type"] == "FloatField":
                fieldData["type"] = "float"
                fieldData["value"] = float(getattr(model_instance,field.name))
            elif fieldData["type"] == "IntegerField":
                fieldData["type"] = "int"
                fieldData["value"] = int(getattr(model_instance,field.name))
            elif fieldData["type"] == "DateField":
                fieldData["type"] = "date"
                fieldData["value"] = str(getattr(model_instance,field.name))
            elif fieldData["type"] == "ForeignKey":
                fieldData["type"] = "select"
                f= getattr(model_instance,field.name)
                fieldData["value"] = str(f.pk)
                fieldData["to_field"] = f"{f._meta.app_label}.{f._meta.object_name}"
                fieldData["values"] = []
                pkObj = importlib.import_module(f"{f._meta.app_label}.models")
                objs = getattr(pkObj,f"{f._meta.object_name}")
                for obj in objs.objects.all():
                    for key in ["name","title","label","slug","domain_fqdn"]:
                        if hasattr(obj,key):
                            strname = str(getattr(obj,key))
                            fieldData["values"].append({"value":str(obj.pk),"label":strname})
                            break


            elif fieldData["type"] == "JSONField":
                fieldData["type"] = "json"
                fieldData["value"] = json.dumps(getattr(model_instance,field.name))
            else:
                fieldData["type"] = "text"

                fieldData["value"] = getattr(model_instance,field.name)
            if field.name in readonly:
                fieldData["readonly"] = True
            retr.append(fieldData)
            chksm += str(getattr(model_instance,field.name))
    m = hashlib.sha512()
    m.update(chksm.encode('utf-8'))
    return retr,m.hexdigest()
