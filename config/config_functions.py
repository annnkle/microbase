import json
from .models import Category


def create_metadata_upload_form(category_names_types, category_values):
    f = open("config/forms_upload.py", "w")
    f.write("from django import forms\n"
            "from theotherapp.forms import MetadataUploadForm\n")

    for category, type in category_names_types.items():
        if type == 'choices':
            f.write("{} = [\n".format(category.upper()))
            for value in category_values[category]:
                f.write("\t('{}', '{}'),\n".format(value, value))
            f.write("]\n\n")
    f.write("class ConfiguredCategories(MetadataUploadForm):\n")

    for category, type in category_names_types.items():
        if type == "text":
            f.write("\t{} = forms.CharField()\n".format(category))
        elif type == "choices":
            f.write("\t{} = forms.ChoiceField(choices={})\n".format(category, category.upper()))
        elif type == "numeric":
            f.write("\t{} = forms.IntegerField()\n".format(category))
    f.close()


def get_cleaned_result(request):
    return list({k: v for k, v in request.items() if k.startswith("form")}.items())


def create_category_dicts(cleaned_data):
    category_names_types = {}
    category_values = {}
    for row in cleaned_data:
        name = row['attribute_name']
        type = row['attribute_type']
        values = row['allowed_values']
        category_names_types[name] = type
        category_values[name] = values
    return category_names_types, category_values


def check_list_for_duplicates(list):
    seen = set()
    dupes = [x for x in list if x.lower() in seen or seen.add(x.lower())]
    return dupes


def list_to_list_of_choices(list):
    choices = []
    for item in list:
        choice = (str(item), str(item))
        choices.append(choice)
    return choices


from functools import wraps
from django.shortcuts import redirect


def pre_config(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):

        config_state = Category.objects.all()
        if not config_state:
            return redirect('config/')
        else:
            return function(request, *args, **kwargs)

    return wrap


def post_config(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        config_state = Category.objects.all()
        if config_state:
            return redirect('/')
        else:
            return function(request, *args, **kwargs)
    return wrap
