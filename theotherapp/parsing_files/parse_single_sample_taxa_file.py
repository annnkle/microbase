from typing import Union

from theotherapp.errors import InvalidTaxaFileError

SINGLE_SAMPLE_TAXA_FILE_COLUMNS_COUNT = 9


def parse_raw_single_sample_taxa_file_line(raw_line: Union[str, bytes]) -> list[str]:
    parsed_line = raw_line
    if isinstance(raw_line, bytes):
        parsed_line = raw_line.decode("utf-8")
    parsed_line = parsed_line.strip("\n")

    tokens = parsed_line.split("\t")

    return tokens


def check_if_single_sample_taxa_file(parsed_line_values: list[str]) -> bool:
    """
    Checks if parsed values of line from file is in single sample taxa file format. 

    Does that by checking if line contains proper number of columns and ends with numeric column.
    """

    if len(parsed_line_values) != SINGLE_SAMPLE_TAXA_FILE_COLUMNS_COUNT:
        return False
    
    if not parsed_line_values[-1].isnumeric():
        return False

    return True


def parse_single_sample_taxa_file(raw_lines: list[Union[str, bytes]]) -> list[dict]:
    taxas_data: list[dict] = []

    for raw_line in raw_lines:
        vals = parse_raw_single_sample_taxa_file_line(raw_line)
        if not check_if_single_sample_taxa_file(vals):
            raise InvalidTaxaFileError()

        taxas_data.append({
            "super_kingdom": vals[0], "kingdom": vals[1], "phylum": vals[2], "klass": vals[3], "order": vals[4],
            "family": vals[5], "genus": vals[6], "species": vals[7], "count": vals[8]
        })
        
    return taxas_data
