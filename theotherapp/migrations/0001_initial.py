# Generated by Django 4.1.5 on 2023-07-04 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='additionals/')),
                ('filename', models.CharField(max_length=255)),
                ('sample_id', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PatientSampleIDs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.CharField(max_length=24)),
                ('sample_id', models.CharField(max_length=24, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Taxa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('super_kingdom', models.CharField(max_length=255)),
                ('kingdom', models.CharField(max_length=255)),
                ('phylum', models.CharField(max_length=255)),
                ('klass', models.CharField(max_length=255)),
                ('order', models.CharField(max_length=255)),
                ('family', models.CharField(max_length=255)),
                ('genus', models.CharField(max_length=255)),
                ('species', models.CharField(max_length=255)),
                ('count', models.IntegerField()),
                ('patient_sample_ids', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='theotherapp.patientsampleids')),
            ],
            options={
                'ordering': ['-count'],
            },
        ),
        migrations.CreateModel(
            name='MetadataRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=255)),
                ('patient_sample_ids', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='theotherapp.patientsampleids')),
            ],
        ),
    ]
