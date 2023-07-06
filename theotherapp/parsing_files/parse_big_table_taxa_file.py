from theotherapp.utils import find_indices
from theotherapp.errors import InvalidTaxaFileError
from theotherapp.taxa import UNIDENTIFIED_TAXA_RANK, TaxonomicRank

from typing import Union

def parse_big_table_taxa_file_header(line: Union[bytes, str]) -> list[str]:
    """
    Parses header into separate cell values.
    """

    if isinstance(line, bytes):
        line = line.decode('utf-8')
    return line.strip('\n').split('\t')

def map_big_table_taxa_file_samples(header: Union[bytes, str], sample_ids: list[str]):
    """
    Parses header to dict where keys are column indexes and values are sample ids.
    """

    parsed_h = parse_big_table_taxa_file_header(header)

    # If there are more samples in taxa file -> raise
    if set(parsed_h[1:]) - set(sample_ids):
        raise InvalidTaxaFileError()

    mapped_samples = {}
    for sample_id in sample_ids:
        col_inds = find_indices(parsed_h, sample_id)
        # Not found OR duplicates OR in first column -> raise
        if not col_inds or len(col_inds) > 1 or col_inds[0] == 0:
            raise InvalidTaxaFileError()
        mapped_samples[col_inds[0]] = sample_id

    return mapped_samples


ORDER = (
    TaxonomicRank.SUPER_KINGDOM,
    TaxonomicRank.KINGDOM,
    TaxonomicRank.PHYLUM,
    TaxonomicRank.KLASS,
    TaxonomicRank.ORDER,
    TaxonomicRank.FAMILY,
    TaxonomicRank.GENUS,
    TaxonomicRank.SPECIES
)


TAXONOMIC_RANK_MAPPING = {
    "sk": TaxonomicRank.SUPER_KINGDOM,
    "k": TaxonomicRank.KINGDOM,
    "p": TaxonomicRank.PHYLUM,
    "c": TaxonomicRank.KLASS,
    "o": TaxonomicRank.ORDER,
    "f": TaxonomicRank.FAMILY,
    "g": TaxonomicRank.GENUS,
    "s": TaxonomicRank.SPECIES,
}


def parse_taxonomic_rank(raw: str):
    return TAXONOMIC_RANK_MAPPING.get(raw)

SEP = "__"

def parse_big_table_taxa_file_taxa_cell(cell: str):
    if not cell:
        raise InvalidTaxaFileError()

    taxa_data = {taxa_rank.value: UNIDENTIFIED_TAXA_RANK for taxa_rank in TaxonomicRank}

    values = cell.split(";")
    for ind, raw_taxa_value in enumerate(values):
        vals = raw_taxa_value.split(SEP)

        if len(vals) != 2:
            raise InvalidTaxaFileError()
        
        rank = parse_taxonomic_rank(vals[0])
        expected_rank = ORDER[ind]
        if rank != expected_rank:
            raise InvalidTaxaFileError()

        if vals[1]:
            taxa_data[rank] = vals[1]

    return taxa_data


def parse_big_table_taxa_file_line(line: Union[str, bytes], mapped_samples: dict[int, str]):
    """
    Parses line from big table taxa file into dict.
    """

    if isinstance(line, bytes):
        line = line.decode('utf-8')

    values = line.strip('\n').split('\t')
    # Header must contain all samples. First cell in header should not contain sample.
    if len(values) != len(mapped_samples) + 1:
        raise InvalidTaxaFileError("Invalid number of columns in taxa file.")

    results = {
        "taxa_data": parse_big_table_taxa_file_taxa_cell(values[0]),
        "counts": {}
    }

    for ind, raw_count in enumerate(values[1:]):
        cell_ind = ind + 1
        sample_id = mapped_samples[cell_ind]
        try:
            count = int(raw_count)
        except ValueError:
            raise InvalidTaxaFileError("Invalid taxa file: count cells must contain integer values.")

        if count > 0:
            results["counts"][sample_id] = count

    return results
