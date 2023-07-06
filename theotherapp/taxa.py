from enum import Enum

UNIDENTIFIED_TAXA_RANK = "unidentified"
UNCLASSIFIED = "unclassified"
UNCULTURED = "uncultured"

class TaxonomicRank(str, Enum):
    SUPER_KINGDOM = "super_kingdom"
    KINGDOM = "kingdom"
    PHYLUM = "phylum"
    KLASS = "klass"
    ORDER = "order"
    FAMILY = "family"
    GENUS = "genus"
    SPECIES = "species"
