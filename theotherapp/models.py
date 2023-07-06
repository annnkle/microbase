from django.db import models
# Create your models here.


class PatientSampleIDs(models.Model):
    patient_id = models.CharField(max_length=24)
    sample_id = models.CharField(max_length=24, unique=True)  # some ids probably have letters in them
    #date_uploaded = models.DateField()


class MetadataRow(models.Model):
    category = models.CharField(max_length=64)
    value = models.CharField(max_length=255)
    patient_sample_ids = models.ForeignKey(PatientSampleIDs, on_delete=models.CASCADE)


class Taxa(models.Model):
    super_kingdom = models.CharField(max_length=255)
    kingdom = models.CharField(max_length=255)
    phylum = models.CharField(max_length=255)
    klass = models.CharField(max_length=255)
    order = models.CharField(max_length=255)
    family = models.CharField(max_length=255)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)

    count = models.IntegerField()
    patient_sample_ids = models.ForeignKey(PatientSampleIDs, on_delete=models.CASCADE)
    #metadata_rows = models.ManyToManyField(MetadataRow)
    class Meta:
        ordering = ['-count']


class AdditionalFile(models.Model):
    file = models.FileField(upload_to='additionals/')
    filename = models.CharField(max_length=255)
    sample_id = models.CharField(max_length=255, blank=True)

