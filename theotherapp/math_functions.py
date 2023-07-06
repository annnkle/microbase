import skbio.diversity as sd
import pandas as pd
import scipy.stats as stats
import numpy
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from collections import defaultdict
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from skbio.stats.ordination import pcoa

def calculate_alpha_diversity(df, group, metric):
    alpha_results = defaultdict(list)
    df = pd.read_json(df)
    sample_list = df['sample_id'].unique()

    for sample in sample_list:
        sample_group = df.loc[df['sample_id'] == sample, group].iloc[0]
        result = sd.alpha_diversity(metric, df.loc[df['sample_id'] == sample]['count'].values)
        alpha_results[sample_group].append(result[0])


    return dict(alpha_results)

def calculate_beta_diversity(df, group, metric):
    df = pd.read_json(df)
    sample_ids_groups = df[['sample_id', group]].drop_duplicates().reset_index()
    df = pd.pivot(df, index='sample_id', columns='taxon', values='count').fillna(0).set_index(sample_ids_groups['sample_id'])
    distance_matrix = sd.beta_diversity(metric, df, ids=df.index)
    pcoa_result = pd.DataFrame(pcoa(distance_matrix).samples.values.T)
    pcoa_result["group"] = sample_ids_groups[group]
    pcoa_result['sample_id'] = sample_ids_groups['sample_id']

    grouped_pcoa = pcoa_result.groupby("group")
    outer = defaultdict(dict)
    for name, group in grouped_pcoa:
        group = group.reset_index(drop=True)
        inner = defaultdict(list)
        if len(group['sample_id']) > 2:
            inner["0"] = list(group[0].values)
            inner["1"] = list(group[1].values)
            inner["2"] = list(group[2].values)
        elif len(group['sample_id']) == 2:
            #FIXME there is no third dimension in this case. The question is whether to showcase this on 3d plot or 2d plot.
            inner["0"] = list(group[0].values)
            inner["1"] = list(group[1].values)
            inner["2"] = [0.0, 0.0]
        else:
            inner["0"] = list(group[0].values)
            inner["1"] = [0.0]
            inner["2"] = [0.0]
        inner["sample_id"] = list(group["sample_id"].values)
        outer[name] = dict(inner)

    return dict(outer)

def calculate_pca(df, group_name):

    labels = df['sample_id']
    label_list = df[["sample_id", group_name]].drop_duplicates().reset_index(drop=True)[group_name]
    # CHECK can we assume that samples stay in the same order after pca (labelling problem)? I think we can...
    df = pd.pivot(df, index='sample_id', columns='taxon', values='count').fillna(0)
    df_scaled = StandardScaler().fit_transform(df)
    pca = PCA(n_components=2)
    principalComponents_data = pca.fit_transform(df_scaled)

    result = pd.concat([label_list, pd.DataFrame(principalComponents_data)], axis=1)
    # convert the dataframe to a dictionary
    result_dict = {}
    for key, group in result.groupby(group_name):
        result_dict[key] = {
            'x': group[0].tolist(),
            'y': group[1].tolist(),
            group_name: str(key) if key != "" and key is not None else "unknown"
        }

    return result_dict

def statistical_significance(measurements):
    labels = measurements.keys()
    n_of_samples = len(numpy.concatenate(list(measurements.values())).flat)
    if n_of_samples > 2:
        results = []
        results.append(stats.f_oneway(*list(measurements.values())))
        pairwise_tukeyhsd()

    elif n_of_samples == 2:
        results = stats

        
    return results, result_label