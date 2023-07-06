import json

def create_metadata_upload_form(category_names_types, category_values):
    f = open("theotherapp/forms.py", "a")
    f.write("\n\n")
    for category, type in category_names_types.items():
        if type == 'choices':
            f.write("{} = [\n".format(category.upper()))
            for value in category_values[category]:
                f.write("\t('{}', '{}'),\n".format(value, value))
            f.write("]\n\n")
    f.write("class MetadataUploadForm(forms.Form):\n")

    for category, type in category_names_types.items():
        if type == "text":
            f.write("\t{} = forms.CharField()\n".format(category))
        elif type == "choices":
            f.write("\t{} = forms.ChoiceField(choices={})\n".format(category, category.upper()))
        elif type == "numeric":
            f.write("\t{} = forms.IntegerField()\n".format(category))
    f.write("\ttaxon_file = forms.FileField()")
    f.close()

def create_config_json(category_names_types):
    category_list_choice_format = []
    for category in list(category_names_types.keys()):
        temp_tuple = tuple((category, category))
        category_list_choice_format.append(temp_tuple)
    # TODO test
    category_list_choice_format.append(tuple(("patient_id", "patient_id")))
    category_list_choice_format.append(tuple(("sample_id", "sample_id")))
    config = {'category_list': list(category_names_types.keys()),
              'category_list_choice_format': category_list_choice_format}

    with open("config.json", "w") as f:
        json.dump(config, f)

def get_cleaned_result(request):
   return list({k: v for k, v in request.items() if k.startswith("form")}.items())

def create_category_dicts(cleaned_result):
    category_names_types = {}
    category_values = {}
    for i in range(0, len(cleaned_result), 3):
        name = cleaned_result[i][1]
        type = cleaned_result[i + 1][1]
        values = cleaned_result[i + 2][1]
        category_names_types[name] = type
        category_values[name] = values.split(", ")
    return category_names_types, category_values

def validate_config(cleaned_result):
    message = ""
    categories_list = []
    duplicates_list = []
    for i in range(0, len(cleaned_result), 3):
        categories_list.append(cleaned_result[i][1])
        if check_list_for_duplicates(cleaned_result[i + 2][1]):
            duplicates_list.append(check_list_for_duplicates(cleaned_result[i + 2][1]))
    if check_list_for_duplicates(categories_list):
        message = "Found duplicate(s) in categories: {}.".format(check_list_for_duplicates(categories_list))
    if duplicates_list:
        message += "Found duplicate(s) in allowed values: {}.".format(duplicates_list)

def check_list_for_duplicates(list):
    seen = set()
    dupes = [x for x in list if x.lower() in seen or seen.add(x.lower())]
    return dupes