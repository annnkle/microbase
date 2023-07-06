from django import forms
from theotherapp.forms import MetadataUploadForm
SPECIES = [
	('cat', 'cat'),
	('dog', 'dog'),
]

class ConfiguredCategories(MetadataUploadForm):
	species = forms.ChoiceField(choices=SPECIES)
