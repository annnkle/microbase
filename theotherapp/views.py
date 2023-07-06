import json

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.transaction import TransactionManagementError
from django.forms import model_to_dict
from django.http import (FileResponse, HttpRequest, HttpResponse,
                         HttpResponseNotFound, JsonResponse, QueryDict)
from django.shortcuts import redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

import theotherapp.forms as forms
from config.config_functions import pre_config
from config.forms_upload import ConfiguredCategories
from config.models import Category
from theotherapp.parsing_files.parse_single_sample_taxa_file import \
    parse_single_sample_taxa_file

from .config_handling_functions import (create_category_dicts,
                                        create_config_json,
                                        create_metadata_upload_form,
                                        get_cleaned_result)
from .errors import (AppError, InvalidTaxaFileError,
                     SampleAlreadyUploadedError, WrongFileFormatError,
                     WrongFileNumberError)
from .file_handling_functions import (parse_contingency_taxon_table,
                                      parse_counts_list_taxonomy_file,
                                      parse_metadata_file, parse_taxonomy_file,
                                      zip_files)
from .math_functions import (calculate_alpha_diversity,
                             calculate_beta_diversity, calculate_pca,
                             statistical_significance)
from .models import AdditionalFile, MetadataRow, PatientSampleIDs, Taxa
from .plotting_functions import (create_dataframe_from_sample_list,
                                 handle_plot_query, parameters_list_to_dict,
                                 run_ggplot_script, send_data_to_csv)
from .querying_functions import (format_queryset, handle_query,
                                 parse_form_input, prepare_query,
                                 remove_prefixes)

configuration_completed = False


@pre_config
def index(request):
    return render(request, 'theotherapp/index.html')

@pre_config
@login_required
def data_upload_view(request):
    category_list = Category.objects.values_list('name', flat=True)

    # form = forms.MetadataUploadForm(request.POST or None)
    form = ConfiguredCategories()

    if request.method == 'POST':
        form = ConfiguredCategories(request.POST, request.FILES)
        # CHECK date format
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    patient_sample_ids = PatientSampleIDs.objects.create(patient_id=data['patient_id'],
                                                                         sample_id=data['sample_id'])
                    for category in category_list:
                        metadata_row_object = MetadataRow.objects.create(category=category,
                                                                         value=request.POST[category],
                                                                         patient_sample_ids=patient_sample_ids)
                        # metadata_row_objects.append(metadata_row_object)
                    taxonomy_annotation_file = request.FILES['taxon_file']
                    taxonomy_annotation_lines = taxonomy_annotation_file.readlines()
                    taxas_data = parse_single_sample_taxa_file(taxonomy_annotation_lines)
                    taxa_objects_to_create = [Taxa(patient_sample_ids=patient_sample_ids, **taxa_data) for taxa_data in taxas_data]
                    Taxa.objects.bulk_create(taxa_objects_to_create, batch_size=1000)

                messages.success(request, "File uploaded successfully!")
                form = ConfiguredCategories(None)
                return render(request, 'theotherapp/data_upload.html', context={'form': form})

            except AppError as e:
                messages.error(request, message=str(e))
                return render(request, 'theotherapp/data_upload.html', context={'form': form})

            except IntegrityError:
                messages.error(request, f"Sample {data['sample_id']} already been uploaded.")
                return render(request, 'theotherapp/data_upload.html', context={'form': form})
                # date_uploaded=date.today())
                # taxa_object.metadata_rows.set(metad`ata_row_objects)

    return render(request, 'theotherapp/data_upload.html', context={'form': form})

@pre_config
@login_required
def multiple_data_upload_view(request):
    form = forms.MultipleMetadataUploadForm()
    category_list = list(Category.objects.all().order_by('pk').values_list('name', flat=True))

    if request.method == 'POST':
        form = forms.MultipleMetadataUploadForm(request.POST, request.FILES)
        metadata_file = request.FILES.get('metadata_file')
        taxonomy_annotation_files = request.FILES.getlist('taxon_files')

        try:
            parsed_metadata = parse_metadata_file(metadata_file, category_list)
            #REFLECT alternatively I can create objects during parsing, but this might make checking for errors more difficult
            with transaction.atomic():
                if len(taxonomy_annotation_files) == len(parsed_metadata):
                    for sample in parsed_metadata.values():
                        patient_sample_ids = PatientSampleIDs.objects.create(patient_id=sample['patient_id'],
                                                                            sample_id=sample['sample_id'])
                        taxonomy_file = [file for file in taxonomy_annotation_files
                                        if file.name == sample['filename']]
                        if len(taxonomy_file) != 1:
                            raise WrongFileNumberError("Duplicated filenames in the metadata file.")
                        else:
                            taxonomy_file_lines = taxonomy_file[0].readlines()
                            try:
                                # Try to parse single sample format
                                parse_taxonomy_file(taxonomy_file_lines, patient_sample_ids)
                            except InvalidTaxaFileError:
                                # Try to parse counts list format
                                parse_counts_list_taxonomy_file(taxonomy_file_lines, patient_sample_ids)
                            for category in category_list:
                                metadata_row_object = MetadataRow.objects.create(category=category,
                                                                                value=sample[category],
                                                                                patient_sample_ids=patient_sample_ids)

                elif len(taxonomy_annotation_files) != len(parsed_metadata) and len(taxonomy_annotation_files) == 1:
                    patient_sample_ids_list = []
                    already_uploaded_samples = []
                    for sample in parsed_metadata.values():
                        if PatientSampleIDs.objects.filter(sample_id=sample['sample_id']).exists():
                            already_uploaded_samples.append(sample['sample_id'])

                        if already_uploaded_samples:
                            continue
                        
                        patient_sample_ids = PatientSampleIDs.objects.create(patient_id=sample['patient_id'],
                                                                        sample_id=sample['sample_id'])

                        patient_sample_ids_list.append(patient_sample_ids)
                        for category in category_list:
                            metadata_row_object = MetadataRow.objects.create(category=category,
                                                                            value=sample[category],
                                                                            patient_sample_ids=patient_sample_ids)

                    if already_uploaded_samples:
                        raise SampleAlreadyUploadedError(f"Samples: {already_uploaded_samples} have already been uploaded.")
                    parse_contingency_taxon_table(taxonomy_annotation_files[0], {psi.sample_id: psi for psi in patient_sample_ids_list})

                else:
                    raise WrongFileNumberError("Wrong number of taxonomy annotation files or wrong metadata file uploaded. "
                                            "Please check your input files and try again. ")
                
                messages.success(request, "File uploaded successfully!")
   
        except AppError as e:
            messages.error(request, str(e))

    #this template and the data_upload template are the exact same for now
    return render(request, 'theotherapp/multiple_data_upload.html', context={'form': form})

@pre_config
@login_required
def browse_view(request):
    all_data = PatientSampleIDs.objects.all().prefetch_related('taxa_set').prefetch_related('metadatarow_set')

    if not all_data.exists():
        messages.info(request, "No data in the database.")
        return render(request, 'theotherapp/browse.html')    

    else:
        paginator = Paginator(all_data, per_page=50)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        page_data = page.object_list
        metadata_categories = [object.category for object in page_data[0].metadatarow_set.all()]
        return render(request, 'theotherapp/browse.html',
                      context={"page": page, "page_data": page_data, "metadata_categories": metadata_categories})

@pre_config
@login_required
def quick_search_view(request):
    sample_id_form = forms.QuickSearchBySampleIDForm(prefix="sample")
    patient_id_form = forms.QuickSearchByPatientIDForm(prefix="patient")
    sample_plot_form = forms.PlotForm(prefix="sample")
    patient_plot_form = forms.PlotForm(prefix="patient")

    if request.GET.get('sample_id_search_button'):
        sample_id_form = forms.QuickSearchBySampleIDForm(request.GET, prefix="sample")
        if sample_id_form.is_valid():
            result_table = handle_query(request.GET, ['sample_id'], format='list', prefix='sample')[0]
            if result_table:
                request.session['result_table'] = (create_dataframe_from_sample_list(
                    result_table,
                    data_parameters={"taxonomic_rank": request.GET["sample-taxonomic_rank"]}
                )).to_json()
                return render(request, 'theotherapp/quick_search.html', context={
                    'sample_id_form': sample_id_form,
                    'patient_id_form': patient_id_form,
                    'sample_plot_form': sample_plot_form,
                    'patient_plot_form': patient_plot_form,
                    'result_table': result_table
                })
            else:
                return render(request, 'theotherapp/quick_search.html', context={
                    'sample_id_form': sample_id_form,
                    'patient_id_form': patient_id_form,
                    'sample_plot_form': sample_plot_form,
                    'patient_plot_form': patient_plot_form,
                    'no_result': True
                })

    if request.GET.get('sample_id_plot_button'):
        sample_id_form = forms.QuickSearchBySampleIDForm(request.GET, prefix="sample")
        sample_plot_form = forms.PlotForm(request.GET, prefix="sample")
        if sample_id_form.is_valid() and sample_plot_form.is_valid():
            sample_data, formatted_query_dict = handle_query(request.GET, ['sample_id'], format='list', prefix='sample')
            # checks if sample is in database
            if sample_data:
                formatted_query_dict['group_by'] = 'sample_id' # no grouping available for these queries
                df, plot_parameters, warning = handle_plot_query(sample_data, formatted_query_dict)
                request.session['plot_parameters'] = plot_parameters
                request.session['df'] = df.to_json()
                return redirect('theotherapp:plot')
            else:
                return render(request, 'theotherapp/quick_search.html', context={
                    'sample_id_form': sample_id_form,
                    'patient_id_form': patient_id_form,
                    'sample_plot_form': sample_plot_form,
                    'patient_plot_form': patient_plot_form,
                    'no_result': True
                })
        else:
            return render(request, 'theotherapp/quick_search.html', context={
                'sample_id_form': sample_id_form,
                'patient_id_form': patient_id_form,
                'sample_plot_form': sample_plot_form,
                'patient_plot_form': patient_plot_form
            })

    if request.GET.get('patient_id_search_button'):
        # FIXME somehow separate the id and plot forms
        patient_id_form = forms.QuickSearchByPatientIDForm(request.GET, prefix="patient")
        if patient_id_form.is_valid():
            result_table = handle_query(request.GET, ['patient_id'], format='list', prefix='patient')[0]
            if result_table:
                request.session['result_table'] = (
                    create_dataframe_from_sample_list(result_table, data_parameters={
                        "taxonomic_rank": request.GET["patient-taxonomic_rank"]
                    })
                ).to_json()
                return render(request, 'theotherapp/quick_search.html', context={
                    'sample_id_form': sample_id_form,
                    'patient_id_form': patient_id_form,
                    'sample_plot_form': sample_plot_form,
                    'patient_plot_form': patient_plot_form,
                    'result_table': result_table
                })
            else:
                return render(request, 'theotherapp/quick_search.html', context={
                    'sample_id_form': sample_id_form,
                    'patient_id_form': patient_id_form,
                    'sample_plot_form': sample_plot_form,
                    'patient_plot_form': patient_plot_form,
                    'no_result': True
                })

    if request.GET.get('patient_id_plot_button'):
        patient_id_form = forms.QuickSearchByPatientIDForm(request.GET, prefix="patient")
        patient_plot_form = forms.PlotForm(request.GET, prefix="patient")
        if patient_id_form.is_valid() and patient_plot_form.is_valid():
            sample_data, formatted_query_dict = handle_query(request.GET, ['patient_id'], format='list',
                                                             prefix='patient')
            # checks if sample is in database
            if sample_data:
                formatted_query_dict['group_by'] = 'patient_id' # no grouping available for these queries
                df, plot_parameters, warning = handle_plot_query(sample_data, formatted_query_dict)
                request.session['plot_parameters'] = plot_parameters
                request.session['df'] = df.to_json()
                return redirect('theotherapp:plot')
            else:
                return render(request, 'theotherapp/quick_search.html', context={
                    'sample_id_form': sample_id_form,
                    'patient_id_form': patient_id_form,
                    'sample_plot_form': sample_plot_form,
                    'patient_plot_form': patient_plot_form,
                    'no_result': True
                })
        else:
            return render(request, 'theotherapp/quick_search.html', context={
                'sample_id_form': sample_id_form,
                'patient_id_form': patient_id_form,
                'sample_plot_form': sample_plot_form,
                'patient_plot_form': patient_plot_form
            })
    if request.GET.get('download_data'):
        json = request.session['result_table']
        df = pd.read_json(json)
        csv_file = df.to_csv(sep=";", index=False)
        response = HttpResponse(csv_file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=plot_data.csv'
        return response

    return render(request, 'theotherapp/quick_search.html', context={
        'sample_id_form': sample_id_form,
        'patient_id_form': patient_id_form,
        'sample_plot_form': sample_plot_form,
        'patient_plot_form': patient_plot_form
    })

@pre_config
@login_required
def advanced_search_view(request):
    def create_forms():
        created_form = forms.GenericForm()
        formset, formset2, formset3 = forms.GenericFormSet(), forms.GenericFormSet(), forms.GenericFormSet()
        formset.id, formset2.id, formset3.id = "formset_1", "formset_2", "formset_3"
        formset.id_button, formset2.id_button, formset3.id_button = "button_formset_1", "button_formset_2", "button_formset_3"
        formset.hidden, formset2.hidden, formset3.hidden = False, True, True
        created_formset_list = [formset, formset2, formset3]

        return created_form, created_formset_list

    query_list = []

    if request.GET.get('form-0-0-user_input'):
        for i in range(3):
            if request.GET.get('form-{0}-0-user_input'.format(i)):
                corrected_user_input = prepare_query(request.GET.items(), form_index=i)
                parsed_user_input = parse_form_input(corrected_user_input)
                query_list.append(parsed_user_input)
        request.session['query_list'] = query_list
        if query_list:
            return redirect('theotherapp:advanced_results')
        else:
            messages.error(request, "No results found.")
            form, formset_list = create_forms()
            return render(request, 'theotherapp/advanced_search.html', {"form": form, "formset_list": formset_list})

    form, formset_list = create_forms()
    return render(request, 'theotherapp/advanced_search.html', context={"form": form, "formset_list": formset_list})


@pre_config
@login_required
def advanced_results_view(request):
    try:
        query_list = request.session['query_list']
    except KeyError:
        print("No query list in session")
    tables_and_visibility_list = []

    '''
        query the database
        TODO account for empty querysets - done?
    '''
    no_results_flag = True
    for query in query_list:
        queryset, query_dict = handle_query(query, list(query.keys()), format='list')
        if not queryset:
            tables_and_visibility_list.append(("hidden", []))
        else:
            no_results_flag = False
            tables_and_visibility_list.append(("visible", queryset))

    if no_results_flag:
        messages.error(request, message="No results found.")
        return redirect('theotherapp:advanced_search')

    '''
        render forms
    '''
    plot_forms = []
    abdiversity_forms = []
    pca_forms = []
    for i in range(len(tables_and_visibility_list)):
        if tables_and_visibility_list[i][0] == 'visible':
            plot_form = forms.PlotForm(prefix=str(i))
            abdiversity_form = forms.DiversityChoiceForm(prefix=str(i))
            pca_form = forms.PCAForm(prefix=str(i))
            plot_forms.append(plot_form)
            abdiversity_forms.append(abdiversity_form)
            pca_forms.append(pca_form)
        else:
            messages.info(request, "No results for query {}".format(i))

    if request.GET.get('download_data_button'):
        csv_list = []
        for i in range(len(tables_and_visibility_list)):
            if tables_and_visibility_list[i][0] == 'visible':
                # CHECK is json -> df -> csv ok?
                df = create_dataframe_from_sample_list(tables_and_visibility_list[i][1],
                data_parameters={"taxonomic_rank": "genus"})
                csv_file = df.to_csv(sep=";", index=False)
                csv_list.append(csv_file)
        archive = zip_files(csv_list, 'plot_data.zip')
        response = HttpResponse(archive, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=plot_data.zip'
        return response

    if request.GET.get('advanced_plot_button'):
        plot_parameters_list = []
        request_values = request.GET

        # Fill forms with submitted data for validation
        plot_forms = []
        warnings = []
        df_list = []

        invalid_plot_form_flag = False
        for i in range(len(tables_and_visibility_list)):
            if tables_and_visibility_list[i][0] == 'visible':
                # TODO? make it a function
                request_values_fragment = {k: v for k, v in request_values.items() if k.startswith(str(i))}
                query_dict = QueryDict('', mutable=True)
                query_dict.update(request_values_fragment)
                plot_form = forms.PlotForm(query_dict, prefix=str(i))
                plot_forms.append(plot_form)

                if plot_form.is_valid():
                    if not invalid_plot_form_flag:
                        parameters = remove_prefixes(request_values, str(i))
                        df, plot_parameters, warning = handle_plot_query(tables_and_visibility_list[i][1], parameters)
                        if warning:
                            # REFLECT what to do with send_data_to_csv in case of a warning
                            warnings.append(i)  # i+1?
                        df_list.append(df.to_json())
                        # moved to plot view
                        # plot_parameters['filename'] = send_data_to_csv(df)
                        plot_parameters_list.append(plot_parameters)
                    else:
                        continue
                else:
                    invalid_plot_form_flag = True
                    continue

        if invalid_plot_form_flag:
            return render(request, 'theotherapp/advanced_results.html',
                          context={'plot_forms': plot_forms,
                                   'abdiversity_forms': abdiversity_forms,
                                   'pca_forms': pca_forms,
                                   'tables_list': tables_and_visibility_list})

        if warnings:
            warning = "Taxon counts for plot(s) {} exceeded max number. Plot(s) may render incorrectly." \
                      "Do you wish to proceed?".format(warnings)

            plot_parameters_dict = parameters_list_to_dict(plot_parameters_list)
            # CHECK do dataframes get left in session and should i care?
            request.session['df_list'] = df_list
            request.session['plot_parameters_dict'] = plot_parameters_dict

            return render(request, 'theotherapp/advanced_results.html',
                          context={'plot_forms': plot_forms,
                                   'abdiversity_forms': abdiversity_forms,
                                   'pca_forms': pca_forms,
                                   'tables_list': tables_and_visibility_list,
                                   'warning': warning})

        plot_parameters_dict = parameters_list_to_dict(plot_parameters_list)
        request.session['df_list'] = df_list
        request.session['plot_parameters_dict'] = plot_parameters_dict

        return redirect('theotherapp:slideshow_plot')

    '''
        warning handling
    '''
    # CHECK is it okay to use input tag this way?
    if request.GET.get('warning_button_yes'):
        return redirect('theotherapp:slideshow_plot')

    if request.GET.get('warning_button_no'):
        return render(request, 'theotherapp/advanced_results.html',
                      context={'plot_forms': plot_forms,
                               'abdiversity_forms': abdiversity_forms,
                               'pca_forms': pca_forms,
                               'tables_list': tables_and_visibility_list})

    '''
        a B diversities
    '''
    if request.GET.get('calculate_diversities_button'):

        alpha_metrics = [v for k, v in request.GET.items() if k.endswith("alpha_metric")]
        beta_metrics = [v for k, v in request.GET.items() if k.endswith("beta_metric")]
        taxonomic_ranks = [v for k, v in request.GET.items() if k.endswith("taxonomic_rank")]
        groups = [v for k, v in request.GET.items() if k.endswith("group")]

        df_list = []
        for i in range(len(tables_and_visibility_list)):
            if tables_and_visibility_list[i][0] == 'visible':
                df = create_dataframe_from_sample_list(
                    sample_list=tables_and_visibility_list[i][1],
                    data_parameters={"taxonomic_rank": taxonomic_ranks[i]}
                )
                df_list.append(df.to_json())
        request.session['df_list'] = df_list
        request.session['alpha_metrics'] = alpha_metrics
        request.session['beta_metrics'] = beta_metrics
        request.session['groups'] = groups

        return redirect('theotherapp:diversity_plot')

    '''
        PCA
    '''
    if request.GET.get('calculate_pca_button'):
        groups = [v for k, v in request.GET.items() if k.endswith("group")]
        taxonomic_ranks = [v for k, v in request.GET.items() if k.endswith("taxonomic_rank")]
        df_list = []
        for i in range(len(tables_and_visibility_list)):
            if tables_and_visibility_list[i][0] == 'visible':
                df = create_dataframe_from_sample_list(
                    sample_list=tables_and_visibility_list[i][1],
                    data_parameters={"taxonomic_rank": taxonomic_ranks[i]}
                )
                df_list.append(df.to_json())
        request.session['df_list'] = df_list
        request.session['groups'] = groups

        return redirect('theotherapp:pca_view')

    return render(request, 'theotherapp/advanced_results.html',
                  context={'plot_forms': plot_forms,
                           'abdiversity_forms': abdiversity_forms,
                           'pca_forms': pca_forms,
                           'tables_list': tables_and_visibility_list})


@pre_config
@login_required
def plot_view(request):
    # REFLECT does try/except fit here?
    df = pd.read_json(request.session['df'])
    plot_parameters = request.session['plot_parameters']
    filename = send_data_to_csv(df)

    plot_parameters['filename'] = filename

    run_ggplot_script(plot_parameters)

    if request.GET.get('download_plot_data'):
        csv_file = df.to_csv(sep=";", index=False)
        response = HttpResponse(csv_file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=plot_data.csv'
        return response

    # FIXME this is a quick fix

    if plot_parameters['interactive'] == 'off':
        return render(request, 'theotherapp/plot.html', {'plot': '{}_plot.svg'.format(plot_parameters['filename'])})
    elif plot_parameters['interactive'] == 'on':
        #with open(f'/home/anna/Desktop/projects/theotherone/media/{filename}_plot.json') as json_data:
        #    plot_json = json.dumps(json.load(json_data))
        #return render(request, 'theotherapp/plot.html', {'plot_json': plot_json})
        #loading plot is done through another view
        return render(request, 'theotherapp/plot.html', {'html_file_name': '{}_plot.html'.format(plot_parameters['filename'])})

@xframe_options_sameorigin
def view_interactive_plot(request: HttpRequest):
    from pathlib import Path

    file_name = request.GET.get("file")
    file_path = Path(settings.MEDIA_ROOT) / file_name

    if file_path.exists():
        with open(file_path, 'r') as file:
            html_content = file.read()
            return render(request, 'theotherapp/view_interactive_plot.html', context={'plot_html': html_content})
    else:
        return HttpResponseNotFound()


@pre_config
@login_required
def slideshow_plot_view(request):
    # TODO anyway there should be some latency in file deletion

    df_list = request.session['df_list']
    plot_parameters_dict = request.session['plot_parameters_dict']
    filenames = []

    for df in df_list:
        # FIXME read json only once
        filename = send_data_to_csv(pd.read_json(df))
        filenames.append(filename)
    plot_parameters_dict['filename'] = " ".join(filenames)

    run_ggplot_script(plot_parameters_dict)

    interactive_list = plot_parameters_dict['interactive'].split(" ")
    # is it ok to add dummy data so that indexes will stay in order?
    plot_list = ['{}_plot.svg'.format(filename) for filename in plot_parameters_dict['filename'].split()]
    html_list = ['{}_plot.html'.format(filename) for filename in plot_parameters_dict['filename'].split()]

    '''
    for filename in plot_parameters_dict['filename'].split():
        # FIXME TEMPORARY WORKAROUND
        try:
            json_data = open('/home/anna/Desktop/projects/theotherone/media/{}_plot.json'.format(filename))
            data = json.load(json_data)
            json.append(data)
            json_data.close()
        except:
            continue
    '''

    if request.GET.get('download_plot_data'):
        csv_list = []
        for df in df_list:
            df = pd.read_json(df)
            csv_file = df.to_csv(sep=";", index=False)
            csv_list.append(csv_file)
        archive = zip_files(csv_list, "plot_data.zip")
        response = HttpResponse(archive, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=plot_data.zip'
        return response

    return render(request, 'theotherapp/slideshow_plot.html',
                  {'plot_list': list(zip(plot_list, html_list, interactive_list)),
                   'height': plot_parameters_dict['height'],
                   'width': plot_parameters_dict['width']})


@pre_config
@login_required
def diversity_plot_view(request):
    df_list = request.session['df_list']
    alpha_metrics = request.session['alpha_metrics']
    beta_metrics = request.session['beta_metrics']
    groups = request.session['groups']

    alpha_list = []
    beta_list = []

    for i, (df, alpha_metric, beta_metric, group) in enumerate(zip(df_list, alpha_metrics, beta_metrics, groups)):
        alpha_data = calculate_alpha_diversity(df, group, metric=alpha_metric)

        # calculate distance matrix AND pcoa
        if len(set(json.loads(df)['sample_id'].values())) == 1:
            beta_list.append("")
            messages.info(request, "Beta diversity not calculated for dataset {}, as that dataset had only one sample".format(i))
        else:
            beta_data = calculate_beta_diversity(df, group, metric=beta_metric)
            beta_list.append(beta_data)
        alpha_list.append(alpha_data)
        #statistical = statistical_significance(alpha_data)


    return render(request, 'theotherapp/diversity_plot.html', context={'alpha_list': alpha_list,
                                                                       'beta_list': beta_list,
                                                                       'groups': groups})


@pre_config
@login_required
def pca_view(request):
    df_list = request.session['df_list']
    groups = request.session['groups']
    pca_list = []
    groups_list = []
    for index, (df, group) in enumerate(zip(df_list, groups)):
        df = pd.read_json(df)
        if len(df['sample_id'].drop_duplicates()) > 1:
            results = calculate_pca(df, group)
            pca_list.append(results)
        else:
            messages.info(request, "Dataset {} had only one sample.".format(index))
    return render(request, 'theotherapp/pca.html', context={'pca_list': pca_list, "groups": groups})


# FIXME fetch does not go through
def delete_temporary_plot_files(request):
    filename = json.loads(request.body.decode("utf-8")).split('/')[-1].rstrip("_plot.svg")
    from pathlib import Path

    media_dir = Path(settings.MEDIA_ROOT)

    extensions = [".csv", "_plot.svg", "_plot.json"]
    removed = []
    not_found = []
    for ext in extensions:
        filename_with_ext = f"{filename}{ext}"
        filepath = media_dir / filename_with_ext
        try:
            filepath.unlink()
            removed.append(filename_with_ext)
        except FileNotFoundError:
            pass

    if not removed:
        return HttpResponseNotFound()
    
    return JsonResponse({"deleted_files": removed})


@pre_config
@login_required
def additional_files_view(request):
    search_sample_form = forms.QuickSearchBySampleIDForm()
    search_name_form = forms.FilenameForm()

    if request.GET.get('search_files'):
        search_sample_form = forms.QuickSearchBySampleIDForm(request.GET)
        if search_sample_form.is_valid():
            '''
                queryset = AdditionalFiles.objects.filter(sample_id=request.GET['sample_id'])
            '''
            ...

    if request.GET.get('search_filenames'):
        search_name_form = forms.FilenameForm(request.GET)
        if search_name_form.is_valid():
            '''
                queryset = AdditionalFile.objects.filter(file=request.GET['file'])
            '''
            ...

    if request.method == 'POST':
        upload_form = forms.AdditionalFileUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            document = upload_form.save()
    else:
        upload_form = forms.AdditionalFileUploadForm()
    return render(request, 'theotherapp/additional_files.html', context={'search_sample_form': search_sample_form,
                                                                         'search_name_form': search_name_form,
                                                                         'upload_form': upload_form})

#def custom_page_not_found_view(request, exception):
#    return render(request, 'theotherapp/404.html')

def custom_error_view(request):
    return render(request, 'theotherapp/error.html')

def custom_bad_request_view(request, exception):
    return render(request, 'theotherapp/bad_request.html')

def custom_permission_denied_view(request, exception):
    return render(request, 'theotherapp/permissiondenied.html')
