import pandas as pd

from theotherapp.plotting_functions import create_dataframe_from_sample_list, parse_parameters, normalize, leave_top_taxa_and_others
import pandas

def test_create_dataframe_from_sample_list():
    assert ...

def test_parse_parameters():
    # REFLECT maybe pass parameters lists as arguments?
    parameters = {'sample_id': '1', 'bar_pie_choice': 'stacked_bar', 'top': '5', 'width': '800', 'height': '600',
     'title': 'Default title', 'x_label': 'Whatever samples', 'y_label': 'Count', 'sample_id_plot_button': 'Plot'}
    assert parse_parameters(parameters) == {'top': '5'}, {'plot_type': 'stacked_bar', 'width': '800', 'height': '600', 'title': 'Default title', 'x_label': 'Whatever samples', 'y_label': 'Count', 'colorscale': 'default', 'interactive': 'off'}

def test_parse_parameters_n_of_values():
    parameters = {'sample_id': '1', 'bar_pie_choice': 'stacked_bar', 'top': '5', 'width': '800', 'height': '600',
                  'title': 'Default title', 'x_label': 'Whatever samples', 'y_label': 'Count',
                  'sample_id_plot_button': 'Plot'}
    data_parameters, plot_parameters = parse_parameters(parameters)
    n_of_v_data = len(data_parameters.values()[0])
    n_of_v_plot = len(plot_parameters.values()[0])
    assert all(len(value) == n_of_v_data for value in data_parameters)
    assert all(len(value) == n_of_v_plot for value in plot_parameters)

def test_normalize():
    data = {
        "sample_id": [1, 1, 1, 2, 2, 2, 3, 3, 3],
        "taxon": ["A", "B", "C", "A", "B", "C", "A", "B", "D"],
        "count": [1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    out_data = {
        "sample_id": [1, 2, 3],
        "taxon": ["A", "A", "A"],
        "count": [1, 4, 7]
    }
    df = pd.DataFrame(data)
    output = pd.DataFrame(out_data)
    assert normalize(df, 0.7) == output

def test_leave_top_taxa_and_others():
    data = {
        "sample_id": [1, 1, 1, 1, 1],
        "taxon": ["A", "B", "C", "D", "E"],
        "count": [12, 40, 55, 2, 5]
    }
    out_data = {
        "sample_id": [1, 1, 1, 1],
        "taxon": ["C", "B", "A", "Others"],
        "count": [55, 40, 12, 7]
    }
    df = pd.DataFrame(data)
    output = pd.DataFrame(out_data)
    assert leave_top_taxa_and_others(df, 3) == output