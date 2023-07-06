from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .config_functions import check_list_for_duplicates

alphanumeric_underscore_rgx = RegexValidator(r'^[0-9a-zA-Z_]*$', 'Only letters, numbers and underscores are allowed.')
alphanumeric_coma_underscore_rgx = RegexValidator(r'^[0-9a-zA-Z_, ]*$', 'Only letters, numbers, comas, spaces and underscores are allowed.')


DATA_TYPES = (
    ("text", "Plain text"),
    ("choices", "Choices"),
    ("numeric", "Numeric"),
    ("date", "Date")
)

def extract_values(string):
    pattern = r'\b\s*([^,\s][^,]*[^,\s])\s*\b'
    matches = re.findall(pattern, string)
    return matches

class ConfigurationForm(forms.Form):
    attribute_name = forms.CharField(max_length=255, validators=[alphanumeric_underscore_rgx])
    attribute_type = forms.ChoiceField(choices=DATA_TYPES)
    allowed_values = forms.CharField(validators=[alphanumeric_coma_underscore_rgx], required=False)

    def clean(self):
        data = self.cleaned_data

        if data['attribute_type'] == "choice" and not data['allowed_values']:
            raise ValidationError('Allowed values must be provided for choices data type.')

        return data

    def clean_allowed_values(self):
        allowed_values =  extract_values(self.cleaned_data["allowed_values"])
        duplicates = check_list_for_duplicates(allowed_values)
        if duplicates:
            raise ValidationError("Found duplicates in allowed values list: {}.".format(duplicates))

        return allowed_values

ConfigurationFormset = forms.formset_factory(ConfigurationForm, extra=0, min_num=1, max_num=16)
