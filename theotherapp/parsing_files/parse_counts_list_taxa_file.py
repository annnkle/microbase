from typing import Union

from theotherapp.errors import InvalidTaxaFileError
from theotherapp.taxa import TaxonomicRank, UNCLASSIFIED, UNCULTURED, UNIDENTIFIED_TAXA_RANK

VALS_ORDER = {
    TaxonomicRank.SUPER_KINGDOM: 1,
    TaxonomicRank.PHYLUM: 2,
    TaxonomicRank.KLASS: 3,
    TaxonomicRank.ORDER: 5,
    TaxonomicRank.FAMILY: 7,
    TaxonomicRank.GENUS: 8,
    TaxonomicRank.SPECIES: 9
}

def parse_counts_list_taxa_file_line(line: Union[str, bytes]):
    if isinstance(line, bytes):
        line = line.decode("utf-8")
    values = line.strip("\n").split("\t")

    # all taxa ranks empty evaluates to all unidentified
    if len(values) < 1 or not values[0].isdigit():
        raise InvalidTaxaFileError()

    taxa_data = {
        taxa_rank.value: UNIDENTIFIED_TAXA_RANK
        for taxa_rank in TaxonomicRank
    }

    for taxa_rank, ind in VALS_ORDER.items():
        try:
            value = values[ind]
        except IndexError:
            # Let not present values be unidentified
            pass

        if value in (UNCLASSIFIED, UNCULTURED):
            continue

        taxa_data[taxa_rank.value] = value

    return taxa_data



def parse_counts_list_taxa_file_counts(lines: list[Union[str,bytes]]):
    taxa_counts = {}
    for line in lines:
        taxa_data = parse_counts_list_taxa_file_line(line)
        taxa_key = tuple(taxa_data.values())
        taxa_counts[taxa_key] = taxa_counts.get(taxa_key, 0) + 1
    return taxa_counts
