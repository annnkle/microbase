import csv
import json
import re
import zipfile
from io import BytesIO

import magic

from config.config_functions import list_to_list_of_choices
from config.models import Category
from theotherapp.errors import InvalidMetadataError, WrongFileFormatError
from theotherapp.models import PatientSampleIDs, Taxa
from theotherapp.parsing_files.parse_big_table_taxa_file import (
    map_big_table_taxa_file_samples, parse_big_table_taxa_file_line)
from theotherapp.parsing_files.parse_counts_list_taxa_file import (
    parse_counts_list_taxa_file_counts, parse_counts_list_taxa_file_line)
from theotherapp.parsing_files.parse_single_sample_taxa_file import \
    parse_single_sample_taxa_file


def get_mime_type(file):
    """
    Get MIME by reading the header of the file
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)
    return mime_type

def zip_files(files, archive_name):
    outfile = BytesIO()
    with zipfile.ZipFile(outfile, 'w') as zf:
        for n, f in enumerate(files):
            zf.writestr("{}.csv".format(n), f)
    return outfile.getvalue()

def dump_queryset_to_json(queryset):
    data_dumpable = []
    for sample in queryset:
        sample_dict = {}
        sample_dict['sample_id'] = sample.sample_id
        sample_dict['patient_id'] = sample.patient_id
        sample_dict['taxa'] = {d['taxon']: d['count'] for d in list(sample.taxa_set.all().values('taxon', 'count'))}
        sample_dict['metadata'] = {d['category']: d['value'] for d in list(sample.metadatarow_set.all().values('category', 'value'))}
        data_dumpable.append(sample_dict)
    return json.dumps(data_dumpable)

def parse_metadata_file(file, category_list):
    def parse_line(line):
        return re.split(r'\s*[,;\t]\s*', line)

    category_list = ['filename', 'sample_id', 'patient_id'] + category_list
    lines_metadata = file.readlines()
    lines_metadata = [line.decode("UTF-8").rstrip("\n") for line in lines_metadata]

    if len(lines_metadata) < 1:
        raise InvalidMetadataError("Uploaded metadata is empty.")

    # Removing CSV header and checking it
    header = parse_line(lines_metadata.pop(0))
    if header != category_list:
        raise InvalidMetadataError("Invalid metadata header. Please check your uploaded file.")

    metadata = {}
    for i in range(0, len(lines_metadata)):
        line = parse_line(lines_metadata[i])
        metadata_obj = {}
        for index, category in enumerate(category_list):
            metadata_obj[category] = line[index]
        metadata[str(i)] = metadata_obj
    return metadata

def parse_taxonomy_file(taxonomy_annotation_lines, patient_sample_ids):
    taxas_data = parse_single_sample_taxa_file(taxonomy_annotation_lines)
    taxa_objects_to_create = [Taxa(patient_sample_ids=patient_sample_ids, **taxa_data) for taxa_data in taxas_data]
    Taxa.objects.bulk_create(taxa_objects_to_create, batch_size=1000)

def create_taxon_object(line, patient_sample_ids):
    if isinstance(line, str):
        values = line.rstrip().split('\t')
    elif isinstance(line, bytes):
        values = line.decode('utf-8').rstrip().split('\t')

    if len(values) != 2:
        raise WrongFileFormatError("Wrong taxonomy classification file format (wrong number of columns).")
    elif not values[1].isnumeric():
        raise WrongFileFormatError(
            "Wrong taxonomy classification file format (last column should contain numbers).")
    else:
        return Taxa(taxon=values[0], count=values[1], patient_sample_ids=patient_sample_ids)

def parse_contingency_taxon_table(file, patient_sample_ids_map: dict[str, PatientSampleIDs]):
    lines = file.readlines()
    header = lines[0]
    mapped_samples = map_big_table_taxa_file_samples(header, list(patient_sample_ids_map.keys()))

    taxa_objects = []

    for line in lines[1:]:
        parsed = parse_big_table_taxa_file_line(line, mapped_samples)
        for sample_id, count in parsed["counts"].items():
            psi = patient_sample_ids_map[sample_id]
            taxa_objects.append(Taxa(patient_sample_ids=psi, count=count, **parsed["taxa_data"]))

    Taxa.objects.bulk_create(taxa_objects, batch_size=1000)


def parse_counts_list_taxonomy_file(lines, patient_sample_ids: PatientSampleIDs):
    taxa_counts = parse_counts_list_taxa_file_counts(lines)
    taxa_objects = [
        Taxa(
            patient_sample_ids=patient_sample_ids,
            count=count,
            # taxa data
            super_kingdom=taxa_key[0],
            kingdom=taxa_key[1],
            phylum=taxa_key[2],
            klass=taxa_key[3],
            order=taxa_key[4],
            family=taxa_key[5],
            genus=taxa_key[6],
            species=taxa_key[7],
        )
        for (taxa_key, count) in taxa_counts.items()
    ]
    Taxa.objects.bulk_create(taxa_objects, batch_size=1000)
