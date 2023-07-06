import pytest

from theotherapp.errors import InvalidTaxaFileError
from theotherapp.parsing_files.parse_big_table_taxa_file import (
    map_big_table_taxa_file_samples, parse_big_table_taxa_file_header,
    parse_big_table_taxa_file_line, parse_big_table_taxa_file_taxa_cell)


@pytest.mark.parametrize(('line', 'expected'), [
    (b"A\tB\tC\tD\n", ["A", "B", "C", "D"]),
    ("A\tB\tC\tD\n", ["A", "B", "C", "D"]),
])
def test_parse_big_table_taxa_file_header(line, expected):
    assert parse_big_table_taxa_file_header(line) == expected


@pytest.mark.parametrize(('header', 'sample_ids', 'expected_mapped'), [
    (b"XYZ\tS1\n", ["S1"], {1: "S1"}),
    (b"XYZ\tS1\tS2\tS3\n", ["S1", "S2", "S3"], {1: "S1", 2: "S2", 3: "S3"})
])
def test_map_big_table_taxa_file_samples_success(header, sample_ids, expected_mapped):
    actual_mapped = map_big_table_taxa_file_samples(header, sample_ids)
    assert actual_mapped == expected_mapped


@pytest.mark.parametrize(('header', 'sample_ids', 'expected_error'), [
    # Duplicate sample_id
    (b"XYZ\tS1\tS1\n", ["S1"], InvalidTaxaFileError),
    # Missing sample_id
    (b"XYZ\tS1\n", ["S1", "S2"], InvalidTaxaFileError),
    # sample_id in first column (not allowed)
    (b"S1\tS2\n", ["S1", "S2"], InvalidTaxaFileError),
    # More samples than provided
    (b"XYZ\tS1\tS2\tS3\n", ["S1", "S2"], InvalidTaxaFileError),
])
def test_map_big_table_taxa_file_samples_failure(header, sample_ids, expected_error):
    with pytest.raises(expected_error):
        map_big_table_taxa_file_samples(header, sample_ids)


@pytest.mark.parametrize(('cell', 'expected_taxa_data'), [
    # Full
    (
        "sk__Bacteria;k__;p__P;c__C;o__O;f__F;g__G;s__S",
        {
            "super_kingdom": "Bacteria",
            "kingdom": "unidentified",
            "phylum": "P",
            "klass": "C",
            "order": "O",
            "family": "F",
            "genus": "G",
            "species": "S"
        }
    ),
    # Partial
    (
        "sk__Bacteria;k__;p__P;c__C;o__O",
        {
            "super_kingdom": "Bacteria",
            "kingdom": "unidentified",
            "phylum": "P",
            "klass": "C",
            "order": "O",
            "family": "unidentified",
            "genus": "unidentified",
            "species": "unidentified"
        }
    ),
    # Empty
    (
        "sk__",
        {
            "super_kingdom": "unidentified",
            "kingdom": "unidentified",
            "phylum": "unidentified",
            "klass": "unidentified",
            "order": "unidentified",
            "family": "unidentified",
            "genus": "unidentified",
            "species": "unidentified"
        }
    ),
])
def test_parse_big_table_taxa_file_taxa_cell_success(cell, expected_taxa_data):
    actual_taxa_data = parse_big_table_taxa_file_taxa_cell(cell)
    assert actual_taxa_data == expected_taxa_data


@pytest.mark.parametrize(('cell', 'expected_error'), [
    # Empty cell
    ("", InvalidTaxaFileError),
    # Invalid order
    ("k__K;sk__SK", InvalidTaxaFileError),
    # Invalid format
    ("sk_SK", InvalidTaxaFileError),
])
def test_parse_big_table_taxa_file_taxa_cell_failure(cell, expected_error):
    with pytest.raises(expected_error):
        parse_big_table_taxa_file_taxa_cell(cell)




@pytest.mark.parametrize(('line', 'mapped_samples', 'expected'), [
    # All counts > 0
    (
        b"sk__Bacteria;k__;p__P;c__C;o__O;f__F;g__G;s__S\t10\t5\t6\n",
        {
            1: "S1",
            2: "S2",
            3: "S3"
        },
        {
            "taxa_data": {
                "super_kingdom": "Bacteria",
                "kingdom": "unidentified",
                "phylum": "P",
                "klass": "C",
                "order": "O",
                "family": "F",
                "genus": "G",
                "species": "S"
            },
            "counts": {
                "S1": 10, "S2": 5, "S3": 6
            }
        }
    ),
    # There are counts == 0
    (
        b"sk__Bacteria;k__;p__P;c__C;o__O;f__F;g__G;s__S\t0\t5\t6\n",
        {
            1: "S1",
            2: "S2",
            3: "S3"
        },
        {
            "taxa_data": {
                "super_kingdom": "Bacteria",
                "kingdom": "unidentified",
                "phylum": "P",
                "klass": "C",
                "order": "O",
                "family": "F",
                "genus": "G",
                "species": "S"
            },
            "counts": {"S2": 5, "S3": 6}
        }
    )
])
def test_parse_big_table_taxa_file_line_success(line, mapped_samples, expected):
    actual = parse_big_table_taxa_file_line(line, mapped_samples)
    assert actual == expected


@pytest.mark.parametrize(('line', 'mapped_samples', 'expected_error'), [
    # Too much cells
    (
        b"sk__Bacteria;k__;p__P;c__C;o__O;f__F;g__G;s__S\t10\t5\t6\t11\n",
        {
            1: "S1",
            2: "S2",
            3: "S3"
        },
        InvalidTaxaFileError
    ),
    # Not enough cells
    (
        b"sk__Bacteria;k__;p__P;c__C;o__O;f__F;g__G;s__S\t10\t5\n",
        {
            1: "S1",
            2: "S2",
            3: "S3"
        },
        InvalidTaxaFileError
    ),
    # Not number in count cell
    (
        b"sk__Bacteria;k__;p__P;c__C;o__O;f__F;g__G;s__S\ta10\t5\t6\n",
        {
            1: "S1",
            2: "S2",
            3: "S3"
        },
        InvalidTaxaFileError
    ),
])
def test_parse_big_table_taxa_file_line_failure(line, mapped_samples, expected_error):
    with pytest.raises(expected_error):
        parse_big_table_taxa_file_line(line, mapped_samples)

