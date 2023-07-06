from django.http import QueryDict

from theotherapp import forms
from theotherapp.plotting_functions import handle_plot_query
from theotherapp.querying_functions import remove_prefixes


def advanced_search_results_fill_plots(request_values, tables_and_visibility_list):
    """

    :param request_values: From request.GET.
    :return:
    """

    plot_parameters_list = []

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
                    warning = True
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
