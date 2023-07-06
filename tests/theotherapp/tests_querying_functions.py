from theotherapp.querying_functions import handle_query, remove_prefixes, prepare_query, correct_user_input_from_form,\
                                            parse_form_input


def test_handle_query():
    assert ...


def test_remove_prefixes():
    query_dict = {"0-A": 1, "0-B": 2}
    assert remove_prefixes(query_dict, "0") == {"A": 1, "B": 2}

def test_parse_form_input():
    corrected_user_input = {'form-0-category': 'catA', 'form-0-user_input': 'A', 'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 1}
    assert parse_form_input(corrected_user_input) == {'catA': ['A']}


# possibly unnecessary

def test_prepare_query():
    user_input = {'form-0-0-category': 'catA', 'form-0-0-user_input': 'A'}
    assert prepare_query() == {'form-0-category': 'catA', 'form-0-user_input': 'A', 'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 1}


def test_correct_user_input_from_form():
    user_input = {'form-0-0-category': 'catA', 'form-0-0-user_input': 'A'}
    assert correct_user_input_from_form(user_input) == {'form-0-category': 'catA', 'form-0-user_input': 'A'}