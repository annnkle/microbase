from django.contrib import admin

# Register your models here.
from .models import MetadataRow, PatientSampleIDs, Taxa, AdditionalFile

@admin.register(PatientSampleIDs)
class PatientSampleIDsAdmin(admin.ModelAdmin):
    pass

@admin.register(MetadataRow)
class MetadataRowAdmin(admin.ModelAdmin):
    pass

@admin.register(AdditionalFile)
class AdditionalFileAdmin(admin.ModelAdmin):
    pass