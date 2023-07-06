import pytest

from theotherapp.errors import InvalidTaxaFileError
from theotherapp.parsing_files.parse_single_sample_taxa_file import (
    check_if_single_sample_taxa_file, parse_raw_single_sample_taxa_file_line,
    parse_single_sample_taxa_file)


@pytest.mark.parametrize(("raw_line", "expected"), [
    ("super_kingdom\tkingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\t13\n", ["super_kingdom", "kingdom", "phylum", "klass", "order", "family", "genus", "species", "13"]),
    (b"super_kingdom\tkingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\t13\n", ["super_kingdom", "kingdom", "phylum", "klass", "order", "family", "genus", "species", "13"]),
])
def test_parse_raw_single_sample_taxa_file_line(raw_line, expected):
    assert parse_raw_single_sample_taxa_file_line(raw_line) == expected


@pytest.mark.parametrize(("first_file_line", "expected"), [
    ("super_kingdom\tkingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\t13".split("\t"), True),
    # Not number at count col
    ("super_kingdom\tkingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\tasd".split("\t"), False),
    # Missing leftmost
    ("kingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\t13".split("\t"), False),
    # Missing inner
    ("super_kingdom\tkingdom\tphylum\tklass\torder\tgenus\tspecies\t13".split("\t"), False),
])
def test_check_if_single_sample_taxa_file(first_file_line, expected):
    assert check_if_single_sample_taxa_file(first_file_line) is expected


def test_parse_single_sample_taxa_file_success():
    expected = [
        {"super_kingdom": "super_kingdom", "kingdom": "kingdom", "phylum": "phylum", "klass": "klass", "order": "order", "family": "family", "genus": "genus", "species": "species", "count": "13"},
        {"super_kingdom": "super_kingdom", "kingdom": "kingdom", "phylum": "phylum", "klass": "klass", "order": "order", "family": "family", "genus": "genus", "species": "species", "count": "14"}
    ]

    parsed_result = parse_single_sample_taxa_file([
        b"super_kingdom\tkingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\t13\n",
        b"super_kingdom\tkingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\t14\n"
    ])

    assert parsed_result == expected


def test_parse_single_sample_taxa_file_failure_last_col_not_numeric():
    invalid_file_data = [b"super_kingdom\tkingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\tasd\n"]
    with pytest.raises(InvalidTaxaFileError):
        parsed_result = parse_single_sample_taxa_file(invalid_file_data)

def test_parse_single_sample_taxa_file_failure_invalid_col_count():
    invalid_file_data = [b"kingdom\tphylum\tklass\torder\tfamily\tgenus\tspecies\t13\n"]
    with pytest.raises(InvalidTaxaFileError):
        parsed_result = parse_single_sample_taxa_file(invalid_file_data)
