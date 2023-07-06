from theotherapp.querying_functions import handle_query


def quick_search_sample_id_search_result():
    assert len(handle_query(request.GET, ['sample_id'], format='list', prefix='patient')[0]) == 1
    assert type(handle_query(request.GET, ['sample_id'], format='list', prefix='patient')[0]) == 'list'


def quick_search_patient_id_search_result():
    assert type(handle_query(request.GET, ['patient_id'], format='list', prefix='patient')[0) == 'list'