import re

import pandas as pd
from django.db.models import Prefetch, Q, QuerySet

from .models import MetadataRow, PatientSampleIDs, Taxa

## IMPORTANT ##
# HANDLE QUERIES FROM DIFFERENT SOURCES IN SEPARATE FUNCTIONS OR MAKE A BIG ONE?
############
################

def handle_query(query_dict, categories, format='queryset', prefix=None):
    queryset = PatientSampleIDs.objects.all()

    if prefix:
        query_dict = remove_prefixes(query_dict, prefix)

    for category in categories:
        value = query_dict[category]
        value_is_list = isinstance(value, list)

        if category in ("sample_id", "patient_id"):
            filter_key = f"{category}{'__in' if value_is_list else ''}"
            queryset = queryset.filter(**{filter_key: value})
        else:
            value_filter_key = f"metadatarow__value{'__in' if value_is_list else ''}"
            queryset = queryset.filter(
                Q(metadatarow__category=category) & Q(**{value_filter_key: value})
            )
    
    # send different categories from front, use them to filter objects and construct tables/dataframes
    queryset = queryset.prefetch_related('taxa_set').prefetch_related('metadatarow_set')
    return format_queryset(queryset, format), query_dict


def remove_prefixes(query_dict, prefix):
    # the if is to make it fit for query_dict from every source: the sample, patient and advanced searches
    # it doesn't really make a difference for the former two
    return {re.sub(r"^{}-".format(prefix), "", k): v for k, v in query_dict.items() if k.startswith(prefix)}


def prepare_query(unparsed_user_input, form_index):
    # gets registration input from form
    user_input_dict = {k: v for k, v in unparsed_user_input if k.startswith("form-{0}".format(form_index))}
    # cleaning registration input
    corrected_res = correct_user_input_from_form(user_input_dict)
    # total forms count
    corrected_res['form-TOTAL_FORMS'] = 1
    # initial forms count
    corrected_res['form-INITIAL_FORMS'] = 1

    return corrected_res


def format_queryset(queryset, format='queryset'):
    if format == 'queryset':
        return queryset
    elif format == 'list':
        return list(queryset)
    elif format == 'dataframe':
        values = ['taxon', 'count']
        return pd.DataFrame(queryset.values(values))


def correct_user_input_from_form(res_from_form):
    corrected_res_from_form = {}
    for k, v in res_from_form.items():
        tokens = k.split("-")
        tokens.pop(1)
        new_key = '-'.join(tokens)
        corrected_res_from_form[new_key] = v
    return corrected_res_from_form


def parse_form_input(user_input):
    """
    Parses form input into dictionary where keys are categories and values are corresponding vals.

    If value contains "," then space chars are removed from it and it is splitted into list of values by ",".
    """
    
    query = {}
    cat = None
    val = None
    for k, v in user_input.items():
        if k.endswith("category"):
            cat = v
        elif k.endswith("user_input"):
            val = v
            if "," in val:
                val = val.replace(" ", "").split(",")
        else:
            continue
        if cat and val:
            query[cat] = val
            cat = None
            val = None
    return query
