import pandas as pd
from django.forms import model_to_dict


def handle_plot_query(sample_data, parameters):
    data_parameters, plot_parameters = parse_parameters(parameters)
    df = create_dataframe_from_sample_list(sample_data, data_parameters)
    # TODO replace?
    warning = False
    taxon_count = df['taxon'].unique().size
    # TODO replace 60 with whatever colors the palette will have
    if taxon_count > 100:
        warning = True
         #return briefly to view, send message to registration that there are not enough colors and proceeding is unadvised
    '''
    # CHECK the column number is arbitrary as hec
    if len(df.groupby(plot_parameters['group_by'])) > 30:
        column_warning = True
    '''
    if data_parameters.get('normalization'):
        if int(data_parameters['normalization']) != 0:
            df = normalize(df, int(data_parameters['normalization']))
    group_by = plot_parameters['group_by']
    if data_parameters['top']:
        if int(data_parameters['top']) == len(df):
             if plot_parameters.get('pool') == 'off':
                df = df.groupby("sample_id", as_index=False)\
                    .apply(lambda x: leave_only_top_taxa(x, len(x)))
                if data_parameters.get('abs_rel') == 'relative':
                    #df['percentage'] = df['count']/df.groupby('sample_id', as_index=False)['count'].transform('sum')
                    df['percentage'] = df['count']/df.groupby('sample_id')['count'].transform('sum').values
             else:
                df = pooled_leave_only_top_taxa(df, int(data_parameters['top']), plot_parameters['group_by'])
                if data_parameters.get('abs_rel') == 'relative':
                    df['percentage'] = df['count']/df.groupby(plot_parameters['group_by'])['count'].transform('sum')
        elif int(data_parameters['top']) < len(df):
            if plot_parameters.get('pool') == 'off':
                df = df.groupby("sample_id", as_index=False)\
                    .apply(lambda x: leave_top_taxa_and_others(x, int(data_parameters['top'])))
                if data_parameters.get('abs_rel') == 'relative':
                    #df['percentage'] = df['count']/df.groupby('sample_id', as_index=False)['count'].transform('sum')
                    df['percentage'] = df['count']/df.groupby('sample_id')['count'].transform('sum').values
            else:
                df = pooled_leave_only_top_taxa(df, int(data_parameters['top']), plot_parameters['group_by'])
                if data_parameters.get('abs_rel') == 'relative':
                    df['percentage'] = df['count']/df.groupby(plot_parameters['group_by'])['count'].transform('sum')
        else:
            # CHECK czy mogę robić takie flagi jeśli chcę przekazać coś użytkownikowi, a nie mam w aktualnym
            #   kontekście dostępu do requestu żeby przesłać normalne django.message, czy jednak powinnam
            #   w takim wypadku przekazywać request do funkcji?
             if plot_parameters.get('pool') == 'off':
                df = df.groupby("sample_id", as_index=False)\
                    .apply(lambda x: leave_only_top_taxa(x, len(x)))
                if data_parameters.get('abs_rel') == 'relative':
                    #df['percentage'] = df['count']/df.groupby('sample_id', as_index=False)['count'].transform('sum')
                    df['percentage'] = df['count']/df.groupby('sample_id')['count'].transform('sum').values
                    # df['count'] = df['percentage']
             else:
                df.sort_values(
                    [group_by, 'count'], ascending=False
                ).groupby(
                    by=[group_by, 'taxon'], as_index=False
                ).sum().sort_values(
                    [group_by, 'count'], ascending=False
                ).groupby(group_by).head(int(data_parameters['top']))
                if data_parameters.get('abs_rel') == 'relative':
                    df['percentage'] = df.groupby(by=group_by)['count'].transform(lambda x: x / x.sum())
             top_too_much = True

    '''
    # UNDER CONSTRUCTION #
    
    if show_patient_ids_with_sample_ids:
        df['sample_id'] = df['sample_id'] + "(" + df['patient_id'] + ")"
    
    '''


    return df, plot_parameters, warning


def create_dataframe_from_sample_list(sample_list, data_parameters: dict):
    out_df = pd.DataFrame()
    rank_type = data_parameters['taxonomic_rank']
    for sample in sample_list:
        taxa_dict = {}
        for taxon in sample.taxa_set.all():
            rank = getattr(taxon, rank_type)
            taxa_dict[rank] = taxa_dict.get(rank, 0) + taxon.count
        df = pd.DataFrame(taxa_dict.items(), columns=['taxon', 'count'])
        for metadata in sample.metadatarow_set.all():
            # removed list() from around metadata.value
            df[metadata.category] = metadata.value
        df['sample_id'] = [sample.sample_id] * len(taxa_dict)
        df['patient_id'] = [sample.patient_id] * len(taxa_dict)
        out_df = pd.concat([out_df, df], ignore_index=True)

    return out_df


def parse_parameters(parameters):
    if 'bar_pie_choice' in parameters:
        plot_type = parameters['bar_pie_choice']
    elif 'bar_heatmap_choice' in parameters:
        plot_type = parameters['bar_heatmap_choice']

    data_parameters_list = ["top", "normalization", "abs_rel", "taxonomic_rank"]# should groupby be kept twice?
    plot_parameters_list = ["colorscale", "width", "height", "title", "x_label", "y_label", "group_by", "interactive", "pool", "abs_rel", "taxonomic_rank"]

    data_parameters = {}
    plot_parameters = {'plot_type': plot_type}
    for param, value in parameters.items():
        if param == 'abs_rel':
            data_parameters[param] = "absolute"
            plot_parameters[param] = "absolute"
            continue
        if param == "taxonomic_rank":
            data_parameters[param] = value
            plot_parameters[param] = value
            continue
        if param in data_parameters_list:
            data_parameters[param] = value
        elif param in plot_parameters_list:
            if param == 'x_label' or param == 'y_label' or param == 'title':
                plot_parameters[param] = "\"" + value + "\""
            else:
                plot_parameters[param] = value

    #TEST HERE
    #check if all parameters have the same number of values
    fill_in_plot_parameters(data_parameters, plot_parameters)

    return data_parameters, plot_parameters

#REFLECT separate function or not?
def fill_in_plot_parameters(data_parameters, plot_parameters):
    if 'colorscale' not in plot_parameters:
        plot_parameters['colorscale'] = "default"
    if 'interactive' not in plot_parameters:
        plot_parameters['interactive'] = "off"
    if 'pool' not in plot_parameters:
        plot_parameters['pool'] = "off"
    if 'abs_rel' not in data_parameters:
        data_parameters['abs_rel'] = 'relative'
    if 'abs_rel' not in plot_parameters:
        plot_parameters['abs_rel'] = 'relative'

def parameters_list_to_dict(parameters_list):
    out_dict = {}
    for k in parameters_list[0].keys():
        out_dict[k] = " ".join(list(out_dict[k] for out_dict in parameters_list))
    return out_dict

def leave_top_taxa_and_others(df, top):
    counts_sum = df['count'].sum()
    df = leave_only_top_taxa(df, top)
    top_sum = df['count'].sum()

    others_row = df.iloc[0]
    others_row['taxon'] = 'Others'
    others_row['count'] = counts_sum - top_sum

    #FIXME
    df.loc[len(df.index)] = others_row


    return df

# CHECK use this in the other function, or write another, without groupby?
def leave_only_top_taxa(df, top):
    return df.sort_values(['sample_id', 'count'], ascending=False).groupby(by='sample_id').head(int(top)).reset_index(drop=True)

#it can be merged with the above function really
def pooled_leave_only_top_taxa(df, top, group_by):
    return df.sort_values(
        [group_by, 'count'], ascending=False
    ).groupby(
        by=[group_by, 'taxon'], as_index=False
    ).sum().sort_values(
        [group_by, 'count'], ascending=False
    ).groupby(group_by).head(int(top))

#TODO test later on many samples
def normalize(df, percent):
    percent = int(percent) / 100
    column_names = df.columns.values
    column_names = list(column_names[column_names != "count"])
    df = df.groupby(column_names, as_index=False, sort=False).sum()
    df_wide = pd.pivot(df, index='sample_id', columns='taxon', values='count').fillna(0)
    col_condition = df_wide[df_wide > 0].count() / df_wide.shape[0] >= percent
    col_condition = list(col_condition[col_condition].index)  # leave only true value
    df2 = df[df['taxon'].isin(col_condition)]

    return df2

def send_data_to_csv(df):
    import uuid
    temp_filename = str(uuid.uuid4())
    df.reset_index(drop=True).to_csv('media/{}.csv'.format(temp_filename), sep=";", index=False)

    return temp_filename

def run_ggplot_script(plot_parameters):
    import os
    os.system('Rscript theotherapp/ggplot_plot.R --filename {} --groupcat {} --plottype {} --height {} --width {} '
              '--title {} --xlab {} --ylab {} --colorscale {} --interactive {} --pool {} --abs_rel {} --taxonomic_rank {}'.format(
                                                                      plot_parameters['filename'], plot_parameters['group_by'],
                                                                      plot_parameters['plot_type'], plot_parameters['height'],
                                                                      plot_parameters['width'], plot_parameters['title'],
                                                                      plot_parameters['x_label'], plot_parameters['y_label'],
                                                                      plot_parameters['colorscale'], plot_parameters['interactive'],
                                                                      plot_parameters['pool'], plot_parameters['abs_rel'], plot_parameters['taxonomic_rank']))
