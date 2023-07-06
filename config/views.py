from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render
from .config_functions import create_category_dicts, create_metadata_upload_form, check_list_for_duplicates, post_config
from config.forms import ConfigurationForm, ConfigurationFormset
from .models import Category, AllowedValues


@post_config
def database_configuration_view(request):
    form = ConfigurationForm()
    formset = ConfigurationFormset()

    if request.method == "POST":
        formset = ConfigurationFormset(request.POST)
        if formset.is_valid():
            category_names_types, category_values = create_category_dicts(formset.cleaned_data)
            if check_list_for_duplicates(list(category_names_types.keys())):
                    duplicates = check_list_for_duplicates(list(category_names_types.keys()))
                    messages.error(request, "Categories {} are duplicates".format(duplicates))
                    return render(request, 'config/database_configuration.html', context={'form': form, 'formset': formset})
            #FIXME debug nie przechodzi za for, nie wiadomo dlaczego
            for name, datatype in category_names_types.items():
                # CHECK sprawdzać obecność duplikatów przy walidacji formularza, czy przy zapisie do bazy?
                try:
                    category_obj = Category.objects.create(name=name, type=datatype)
                    if name in category_values.keys():
                        for value in category_values[name]:
                            AllowedValues.objects.create(category=category_obj, value=value)
                except IntegrityError:
                    messages.error(request, "Category name has been duplicated")
                    return render(request, 'config/database_configuration.html', context={'form': form, 'formset': formset})
            create_metadata_upload_form(category_names_types, category_values)
            messages.success(request, "Database configured successfully!")
            return render(request, 'config/database_configuration.html',
                          context={'form': form, 'formset': formset})


    return render(request, 'config/database_configuration.html', context={'form': form, 'formset': formset})
