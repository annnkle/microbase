import pytest

from theotherapp.errors import InvalidTaxaFileError
from theotherapp.parsing_files.parse_counts_list_taxa_file import (
    parse_counts_list_taxa_file_counts, parse_counts_list_taxa_file_line)
from theotherapp.taxa import UNIDENTIFIED_TAXA_RANK, TaxonomicRank


@pytest.mark.parametrize(('line', 'expected'), [
    # all filled
    (
        b'1\tsk\tp\tc\tsubc\to\tsubo\tf\tg\ts\tstrain\n',
        {
            TaxonomicRank.SUPER_KINGDOM.value: "sk",
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: "p",
            TaxonomicRank.KLASS.value: "c",
            TaxonomicRank.ORDER.value: "o",
            TaxonomicRank.FAMILY.value: "f",
            TaxonomicRank.GENUS.value: "g",
            TaxonomicRank.SPECIES.value: "s",
        }
    ),
    # all filled, no strain
    (
        b'1\tsk\tp\tc\tsubc\to\tsubo\tf\tg\ts\n',
        {
            TaxonomicRank.SUPER_KINGDOM.value: "sk",
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: "p",
            TaxonomicRank.KLASS.value: "c",
            TaxonomicRank.ORDER.value: "o",
            TaxonomicRank.FAMILY.value: "f",
            TaxonomicRank.GENUS.value: "g",
            TaxonomicRank.SPECIES.value: "s",
        }
    ),
    # just super kingdom
    (
        b'1\nsk',
        {
            TaxonomicRank.SUPER_KINGDOM.value: "sk",
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.KLASS.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.ORDER.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.FAMILY.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.GENUS.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.SPECIES.value: UNIDENTIFIED_TAXA_RANK,
        }
    ),
    # empty, just number
    (
        b'1\n',
        {
            TaxonomicRank.SUPER_KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.KLASS.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.ORDER.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.FAMILY.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.GENUS.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.SPECIES.value: UNIDENTIFIED_TAXA_RANK,
        }
    ),
    # parses unclassified, uncultured
    (
        b'1\tsk\tuncultured\tunclassified\tsubc\tuncultured\tunclassified\tuncultured\tunclassified\tuncultured\tstrain\n',
        {
            TaxonomicRank.SUPER_KINGDOM.value: "sk",
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.KLASS.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.ORDER.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.FAMILY.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.GENUS.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.SPECIES.value: UNIDENTIFIED_TAXA_RANK
        }
    ),
    # real data 1
    (
        b'1\tBacteria\tFirmicutes\tBacilli\tunclassified\tLactobacillales\tunclassified\tStreptococcaceae\tStreptococcus\tuncultured\tELU0035-T194-S-NIPCRAMgANb_000547\n',
        {
            TaxonomicRank.SUPER_KINGDOM.value: "Bacteria",
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: "Firmicutes",
            TaxonomicRank.KLASS.value: "Bacilli",
            TaxonomicRank.ORDER.value: "Lactobacillales",
            TaxonomicRank.FAMILY.value: "Streptococcaceae",
            TaxonomicRank.GENUS.value: "Streptococcus",
            TaxonomicRank.SPECIES.value: UNIDENTIFIED_TAXA_RANK,
        }
    ),
    # real data 2
    (
        b'1\tBacteria\tFirmicutes\tBacilli\tunclassified\tBacillales\tunclassified\tStaphylococcaceae\tStaphylococcus\tStaphylococcus epidermidis\tCU22\n',
        {
            TaxonomicRank.SUPER_KINGDOM.value: "Bacteria",
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: "Firmicutes",
            TaxonomicRank.KLASS.value: "Bacilli",
            TaxonomicRank.ORDER.value: "Bacillales",
            TaxonomicRank.FAMILY.value: "Staphylococcaceae",
            TaxonomicRank.GENUS.value: "Staphylococcus",
            TaxonomicRank.SPECIES.value: "Staphylococcus epidermidis",
        }
    ),
    # real data 2, no strain
    (
        b'1\tBacteria\tFirmicutes\tBacilli\tunclassified\tBacillales\tunclassified\tStaphylococcaceae\tStaphylococcus\tStaphylococcus epidermidis\n',
        {
            TaxonomicRank.SUPER_KINGDOM.value: "Bacteria",
            TaxonomicRank.KINGDOM.value: UNIDENTIFIED_TAXA_RANK,
            TaxonomicRank.PHYLUM.value: "Firmicutes",
            TaxonomicRank.KLASS.value: "Bacilli",
            TaxonomicRank.ORDER.value: "Bacillales",
            TaxonomicRank.FAMILY.value: "Staphylococcaceae",
            TaxonomicRank.GENUS.value: "Staphylococcus",
            TaxonomicRank.SPECIES.value: "Staphylococcus epidermidis",
        }
    ),
])
def test_parse_counts_list_taxa_file_line_success(line, expected):
    actual = parse_counts_list_taxa_file_line(line)
    assert actual == expected




@pytest.mark.parametrize('line', [
    # first column not number
    b'NOT_NUM\tsk\tp\tc\tsubc\to\tsubo\tf\tg\ts\tstrain\n'
])
def test_parse_counts_list_taxa_file_line_success(line):
    with pytest.raises(InvalidTaxaFileError):
        parse_counts_list_taxa_file_line(line)



def test_parse_counts_list_taxa_file_counts_success():
    lines = [
        b'1\tsk\tp\tc\tsubc\to\tsubo\tf\tg\ts\tstrain\n',
        b'1\tsk\tp\tc\tsubc\to\tsubo\tf\tg\ts\tstrain\n',
        b'1\tsk\tp\tc\tsubc\to\tsubo\tf\tg\ts2\tstrain\n',
    ]

    expected = {
        ('sk', 'unidentified', 'p', 'c', 'o', 'f', 'g', 's'): 2,
        ('sk', 'unidentified', 'p', 'c', 'o', 'f', 'g', 's2'): 1
    }

    actual = parse_counts_list_taxa_file_counts(lines)
    assert actual == expected
