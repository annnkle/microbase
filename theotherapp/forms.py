from django import forms
from django.core.exceptions import ValidationError
from theotherapp.models import AdditionalFile
from theotherapp.taxa import TaxonomicRank
from config.models import Category
from .file_handling_functions import get_mime_type
from config.config_functions import list_to_list_of_choices
from django.core.validators import RegexValidator

import json

DATA_TYPES = (
    ("text", "Plain text"),
    ("choices", "Choices"),
    ("numeric", "Numeric"),
    ("date", "Date")
)
'''
COLORSCALES = (
    ("Spectral", "Rainbow"),
    ("RdYlGn", "Red-yellow-green"),
    ("RdYlBu", "Red-yellow-blue"),
    ("RdGy", "Red-grey"),
    ("RdBu", "Red-blue"),
    ("PuOr", "Purple-orange"),
    ("PRGn", "Purple-green"),
    ("PiYG", "Pink-green"),
    ("BrBG", "Brown-blue")
)
'''

COLORSCALES = (
    ("YlOrRd", "Yellow-orange-red"),
    ("YlGnBu", "Yellow-green-blue"),
    ("YlGn", "Yellow-green"),
    ("RdPu", "Red-purple"),
    ("Reds", "Reds"),
    ("Oranges", "Oranges"),
    ("Greens", "Greens"),
    ("Blues", "Blues")
)

ALPHA_DIVERSITY_METRICS = (
    ('chao1', 'chao1'), ('chao1_ci', 'chao1_ci'), ('shannon', 'shannon'), ('simpson', 'simpson'),
    ('simpson_e', 'simpson_e')
)

BETA_DIVERSITY_METRICS = (
    ('braycurtis', 'braycurtis'), ('euclidean', 'euclidean'),
    ('hamming', 'hamming'), ('jaccard', 'jaccard'), ('jensenshannon', 'jensenshannon')
)

category_list = list_to_list_of_choices(list(Category.objects.values_list('name', flat=True)) + ['patient_id', 'sample_id'])

class QuickSearchByPatientIDForm(forms.Form):
    patient_id = forms.CharField()


class QuickSearchBySampleIDForm(forms.Form):
    sample_id = forms.CharField()


TAXONOMIC_RANK_CHOICES = tuple(
    (rank.value, " ".join(rank.split("_"))) for rank in TaxonomicRank
)

class PlotForm(forms.Form):
    # REFLECT maybe there is a way to set required=false everywhere
    group_by = forms.ChoiceField(choices=category_list, required=False)
    top = forms.IntegerField(min_value=5, max_value=10, initial=5, required=False)
    normalization = forms.IntegerField(min_value=0, max_value=100, initial=0, required=False)
    taxonomic_rank = forms.ChoiceField(choices=TAXONOMIC_RANK_CHOICES, initial=TaxonomicRank.GENUS.value)
    colorscale = forms.ChoiceField(choices=COLORSCALES, required=False)
    width = forms.IntegerField(initial=800, required=False)
    height = forms.IntegerField(initial=600, required=False)
    title = forms.CharField(max_length=65, required=True, initial="Default title")
    x_label = forms.CharField(max_length=65, required=True, initial="Some samples")
    y_label = forms.CharField(max_length=65, required=True, initial="Count")
    interactive = forms.BooleanField(required=False, widget=forms.CheckboxInput)
    pool = forms.BooleanField(required=False, widget=forms.CheckboxInput, label="Pool samples")
    abs_rel = forms.BooleanField(required=False, widget=forms.CheckboxInput)
    # MIGHT BE A TEMPORARY FIX
    bar_pie_choice = forms.ChoiceField(choices=(('stacked_bar', 'Stacked bar plot'),
                                                ('pie', 'Pie chart')), widget=forms.RadioSelect, required=False)
    bar_heatmap_choice = forms.ChoiceField(choices=(('stacked_bar', 'Stacked bar plot'),
                                                    ('heatmap', 'Heatmap')), widget=forms.RadioSelect, required=False)

    # should I override is_valid or keep as is?
    def clean_interactive(self):
        interactive = self.cleaned_data.get('interactive')

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("bar_pie_choice") and not cleaned_data.get("bar_heatmap_choice"):
            raise ValidationError("Select a plot type.")


'''
# --- BAR CHOICES PLAYGROUND

def create_plot_form_class(bar_choices: list[tuple[str, str]]):
	class GenericPlotForm(forms.Form):
		group_by = forms.ChoiceField(choices=category_list, required=False)
		top = forms.IntegerField(min_value=5, max_value=10, required=False)
		
		bar_choice = forms.ChoiceField(choices=bar_choices, widget=forms.RadioSelect)
		
	return GenericPlotForm


HeatmapPlotForm = create_plot_form_class([('heatmap', 'Heatmap')])
PiePlotForm = create_plot_form_class([('pie', 'Pie chart')])

heatmapPlotFormInstance = HeatmapPlotForm()
piePlotFormInstance = PiePlotForm()

# --- BAR CHOICES PLAYGROUND END
'''


class GenericForm(forms.Form):
    category = forms.ChoiceField(choices=category_list, label="")
    user_input = forms.CharField(max_length=255, label="", required=True)


GenericFormSet = forms.formset_factory(GenericForm)


class DiversityChoiceForm(forms.Form):
    alpha_metric = forms.ChoiceField(choices=ALPHA_DIVERSITY_METRICS)
    beta_metric = forms.ChoiceField(choices=BETA_DIVERSITY_METRICS)
    taxonomic_rank = forms.ChoiceField(choices=TAXONOMIC_RANK_CHOICES, initial=TaxonomicRank.GENUS.value)
    group = forms.ChoiceField(choices=category_list, label="Group by:")


# CHECK this
class PCAForm(forms.Form):
    group = forms.ChoiceField(choices=category_list, label="Group by:")
    taxonomic_rank = forms.ChoiceField(choices=TAXONOMIC_RANK_CHOICES, initial=TaxonomicRank.GENUS.value)

alphanumeric_underscore_rgx = RegexValidator(r'^[0-9a-zA-Z_ ]*$', 'Only letters, numbers and underscores are allowed.')

class MetadataUploadForm(forms.Form):
    patient_id = forms.CharField(validators=[alphanumeric_underscore_rgx])
    sample_id = forms.CharField(validators=[alphanumeric_underscore_rgx])
    taxon_file = forms.FileField()
    #additional_files = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def clean_taxon_file(self):
        taxon_file = self.cleaned_data['taxon_file']
        mime_type = get_mime_type(taxon_file)
        if mime_type not in ['text/csv', 'text/plain', 'text/tab-separated-values']:
            raise ValidationError("Wrong file type.")
        return taxon_file

    '''
    def clean_additional_files(self):
        additional_files = self.cleaned_data['additional_files']
        if additional_files:
            for file in additional_files:
                mime_type = get_mime_type(file)
                if mime_type not in ['text/csv', 'text/plain', 'text/tab-separated-values', 'application/msword',
                                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                     'application/vnd.oasis.opendocument.spreadsheet',
                                     'application/vnd.oasis.opendocument.text',
                                     'application/pdf', 'application/vnd.ms-excel',
                                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                     'chemical/seq-aa-fasta', 'chemical/seq-na-fasta', 'chemical/seq-na-fastq']:
                    raise ValidationError("Wrong file type.")
        return additional_files
    '''

class MultipleMetadataUploadForm(forms.Form):
    metadata_file = forms.FileField(required=True)
    taxon_files = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'multiple': True}))

class AdditionalFileUploadForm(forms.Form):
    sample_id = forms.CharField(required=False)
    file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def save(self):
        data = self.cleaned_data
        file = theotherapp.models.AdditionalFile(file=data['file'], filename=data['file'].name, sample_id=data.get('sample_id'))
        file.save()

class FilenameForm(forms.Form):
    filename = forms.CharField(required=True)