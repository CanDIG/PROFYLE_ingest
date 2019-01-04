#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
profyle_ingest.py - Creates a new ga4gh dataset and parses profyle metadata
information into it. It populates Individual, Biosample, Experiment and
Analysis objects.

Usage:
  profyle_ingest.py <repo_filename> <dataset_name> <metadata_json>

Options:
  -h --help        Show this screen
  -v --version     Version
  <repo_filename>  Path and filename of the ga4gh repository
  <dataset_name>   Dataset name
  <metadata_json>  Path and filename information to the metadata json file.

"""

import json
import os
from docopt import docopt

import ga4gh.server.datarepo as repo
import ga4gh.server.exceptions as exceptions

from ga4gh.server.datamodel.datasets import Dataset
from ga4gh.server.datamodel.bio_metadata import Individual
from ga4gh.server.datamodel.bio_metadata import Biosample
from ga4gh.server.datamodel.clinical_metadata import Patient
from ga4gh.server.datamodel.clinical_metadata import Enrollment
from ga4gh.server.datamodel.clinical_metadata import Consent
from ga4gh.server.datamodel.clinical_metadata import Diagnosis
from ga4gh.server.datamodel.clinical_metadata import Sample
from ga4gh.server.datamodel.clinical_metadata import Treatment
from ga4gh.server.datamodel.clinical_metadata import Outcome
from ga4gh.server.datamodel.clinical_metadata import Complication
from ga4gh.server.datamodel.clinical_metadata import Tumourboard
from ga4gh.server.datamodel.clinical_metadata import Chemotherapy
from ga4gh.server.datamodel.clinical_metadata import Radiotherapy
from ga4gh.server.datamodel.clinical_metadata import Immunotherapy
from ga4gh.server.datamodel.clinical_metadata import Surgery
from ga4gh.server.datamodel.clinical_metadata import Celltransplant
from ga4gh.server.datamodel.clinical_metadata import Slide
from ga4gh.server.datamodel.clinical_metadata import Study
from ga4gh.server.datamodel.clinical_metadata import Labtest
from ga4gh.server.datamodel.bio_metadata import Experiment
from ga4gh.server.datamodel.bio_metadata import Analysis
from ga4gh.server.datamodel.pipeline_metadata import Extraction
from ga4gh.server.datamodel.pipeline_metadata import Sequencing
from ga4gh.server.datamodel.pipeline_metadata import Alignment
from ga4gh.server.datamodel.pipeline_metadata import VariantCalling
from ga4gh.server.datamodel.pipeline_metadata import FusionDetection
from ga4gh.server.datamodel.pipeline_metadata import ExpressionAnalysis


class GA4GHRepo(object):
    def __init__(self, filename):
        self._filename = filename
        self._repo = None

        self.clinical_metadata_map = {
            'Patient': {
                'table': Patient,
                'local_id': ['patientId'],
                'repo_add': self.add_patient
            },
            'Enrollment': {
                'table': Enrollment,
                'local_id': ["patientId", "enrollmentApprovalDate"],
                'repo_add': self.add_enrollment
            },
            'Consent': {
                'table': Consent,
                'local_id': ["patientId", "consentDate"],
                'repo_add': self.add_consent
            },
            'Diagnosis': {
                'table': Diagnosis,
                'local_id': ["patientId", "diagnosisDate"],
                'repo_add': self.add_diagnosis
            },
            'Sample': {
                'table': Sample,
                'local_id': ["patientId", "sampleId"],
                'repo_add': self.add_sample
            },
            'Treatment': {
                'table': Treatment,
                'local_id': ["patientId", "startDate"],
                'repo_add': self.add_treatment
            },
            'Outcome': {
                'table': Outcome,
                'local_id': ["patientId", "dateOfAssessment"],
                'repo_add': self.add_outcome
            },
            'Complication': {
                'table': Complication,
                'local_id': ["patientId", "date"],
                'repo_add': self.add_complication
            },
            'Tumourboard': {
                'table': Tumourboard,
                'local_id': ["patientId", "dateOfMolecularTumorBoard"],
                'repo_add': self.add_tumourboard
            },
            'Chemotherapy': {
                'table': Chemotherapy,
                'local_id': ["treatmentPlanId", "systematicTherapyAgentName"],
                'repo_add': self.add_chemotherapy
            },
            'Radiotherapy': {
                'table': Radiotherapy,
                'local_id': ["treatmentPlanId", "startDate"],
                'repo_add': self.add_radiotherapy
            },
            'Immunotherapy': {
                'table': Immunotherapy,
                'local_id': ["treatmentPlanId", "startDate"],
                'repo_add': self.add_immunotherapy
            },
            'Surgery': {
                'table': Surgery,
                'local_id': ["treatmentPlanId", "startDate"],
                'repo_add': self.add_surgery
            },
            'Celltransplant': {
                'table': Celltransplant,
                'local_id': ["treatmentPlanId", "startDate"],
                'repo_add': self.add_celltransplant
            },
            'Slide': {
                'table': Slide,
                'local_id': ["patientId", "slideId"],
                'repo_add': self.add_slide
            },
            'Study': {
                'table': Study,
                'local_id': ["patientId", "startDate"],
                'repo_add': self.add_study
            },
            'Labtest': {
                'table': Labtest,
                'local_id': ["patientId", "startDate"],
                'repo_add': self.add_labtest
            }
        }
        self.pipeline_metadata_map = {
            'Extraction': {
                'table': Extraction,
                'local_id': ["sampleId", "extractionId"],
                'repo_add': self.add_extraction
            },
            'Sequencing': {
                'table': Sequencing,
                'local_id': ["sampleId", "sequencingId"],
                'repo_add': self.add_sequencing
            },
            'Alignment': {
                'table': Alignment,
                'local_id': ["sampleId", "alignmentId"],
                'repo_add': self.add_alignment
            },
            'VariantCalling': {
                'table': VariantCalling,
                'local_id': ["sampleId", "variantCallingId"],
                'repo_add': self.add_variant_calling
            },
            'FusionDetection': {
                'table': FusionDetection,
                'local_id': ["sampleId", "fusionDetectionId"],
                'repo_add': self.add_fusion_detection
            },
            'ExpressionAnalysis': {
                'table': ExpressionAnalysis,
                'local_id': ["sampleId", "expressionAnalysisId"],
                'repo_add': self.add_expression_analysis
            }
        }

    def __enter__(self):
        self._repo = repo.SqlDataRepository(self._filename)
        self._repo.open(repo.MODE_WRITE)

        if not os.path.isfile(self._filename):
            self._repo.initialise()

        return self

    def __exit__(self, extype, value, traceback):
        self._repo.commit()
        self._repo.verify()
        self._repo.close()

    def add_dataset(self, dataset):
        self._repo.insertDataset(dataset)
        self._repo.commit()
        self._repo.verify()

    def add_patient(self, patient):
        self._repo.insertPatient(patient)
        self._repo.commit()
        self._repo.verify()

    def add_enrollment(self, enrollment):
        self._repo.insertEnrollment(enrollment)
        self._repo.commit()
        self._repo.verify()

    def add_consent(self, consent):
        self._repo.insertConsent(consent)
        self._repo.commit()
        self._repo.verify()

    def add_diagnosis(self, diagnosis):
        self._repo.insertDiagnosis(diagnosis)
        self._repo.commit()
        self._repo.verify()

    def add_sample(self, sample):
        self._repo.insertSample(sample)
        self._repo.commit()
        self._repo.verify()

    def add_treatment(self, treatment):
        self._repo.insertTreatment(treatment)
        self._repo.commit()
        self._repo.verify()

    def add_outcome(self, outcome):
        self._repo.insertOutcome(outcome)
        self._repo.commit()
        self._repo.verify()

    def add_complication(self, complication):
        self._repo.insertComplication(complication)
        self._repo.commit()
        self._repo.verify()

    def add_tumourboard(self, tumourboard):
        self._repo.insertTumourboard(tumourboard)
        self._repo.commit()
        self._repo.verify()

    def add_chemotherapy(self, chemotherapy):
        self._repo.insertChemotherapy(chemotherapy)
        self._repo.commit()
        self._repo.verify()

    def add_radiotherapy(self, radiotherapy):
        self._repo.insertRadiotherapy(radiotherapy)
        self._repo.commit()
        self._repo.verify()

    def add_immunotherapy(self, immunotherapy):
        self._repo.insertImmunotherapy(immunotherapy)
        self._repo.commit()
        self._repo.verify()

    def add_surgery(self, surgery):
        self._repo.insertSurgery(surgery)
        self._repo.commit()
        self._repo.verify()

    def add_celltransplant(self, celltransplant):
        self._repo.insertCelltransplant(celltransplant)
        self._repo.commit()
        self._repo.verify()

    def add_slide(self, slide):
        self._repo.insertSlide(slide)
        self._repo.commit()
        self._repo.verify()

    def add_study(self, study):
        self._repo.insertStudy(study)
        self._repo.commit()
        self._repo.verify()

    def add_labtest(self, labtest):
        self._repo.insertLabtest(labtest)
        self._repo.commit()
        self._repo.verify()

    def add_individual(self, person):
        self._repo.insertIndividual(person)
        self._repo.commit()
        self._repo.verify()

    def add_biosample(self, biosample):
        self._repo.insertBiosample(biosample)
        self._repo.commit()
        self._repo.verify()

    def add_experiment(self, experiment):
        self._repo.insertExperiment(experiment)
        self._repo.commit()
        self._repo.verify()

    def add_analysis(self, analysis):
        self._repo.insertAnalysis(analysis)
        self._repo.commit()
        self._repo.verify()

    def add_extraction(self, extraction):
        self._repo.insertExtraction(extraction)
        self._repo.commit()
        self._repo.verify()

    def add_sequencing(self, sequencing):
        self._repo.insertSequencing(sequencing)
        self._repo.commit()
        self._repo.verify()

    def add_alignment(self, alignment):
        self._repo.insertAlignment(alignment)
        self._repo.commit()
        self._repo.verify()

    def add_variant_calling(self, variant_calling):
        self._repo.insertVariantCalling(variant_calling)
        self._repo.commit()
        self._repo.verify()

    def add_fusion_detection(self, fusion_detection):
        self._repo.insertFusionDetection(fusion_detection)
        self._repo.commit()
        self._repo.verify()

    def add_expression_analysis(self, expression_analysis):
        self._repo.insertExpressionAnalysis(expression_analysis)
        self._repo.commit()
        self._repo.verify()

def main():
    """
    """
    # Parse arguments
    args = docopt(__doc__, version='profyle ingest 0.1')
    # Handle the passed arguments
    repo_filename = args['<repo_filename>']
    dataset_name = args['<dataset_name>']
    metadata_json = args['<metadata_json>']
    # Read and parse profyle metadata json
    with open(metadata_json, 'r') as json_datafile:
        metadata = json.load(json_datafile, 'UTF-8')
    # Create a dataset
    dataset = Dataset(dataset_name)
    dataset.setDescription('METADATA TEST SERVER')
    # Open and load the data
    with GA4GHRepo(repo_filename) as repo:
        # Add dataset
        try:
            repo.add_dataset(dataset)
        except exceptions.DuplicateNameException:
            pass

        metadata_map = {
            'metadata': repo.clinical_metadata_map,
            'pipeline_metadata': repo.pipeline_metadata_map
        }
        metadata_key = metadata.keys()[0]

        # Iterate through metadata file type based on key and update the dataset
        for individual in metadata[metadata_key]:

            for table in individual:
                if table in metadata_map[metadata_key]:
                    record = individual[table]
                    local_id_list = []
                    for x in metadata_map[metadata_key][table]['local_id']:
                        if record.get(x):
                            local_id_list.append(record[x])
                        else:
                            local_id_list = None
                            print("Skipped: Missing 1 or more primary identifiers for record in: {0} needs {1}".format(
                                table, metadata_map[metadata_key][table]['local_id']))
                            break
                    if not local_id_list:
                        continue

                    local_id = "_".join(local_id_list)

                    obj = metadata_map[metadata_key][table]['table'](dataset, localId=local_id)
                    repo_obj = obj.populateFromJson(json.dumps(record))

                    # Add object into the repo file
                    try:
                        metadata_map[metadata_key][table]['repo_add'](repo_obj)
                    except exceptions.DuplicateNameException:
                        print("Skipped: Duplicate {0} detected for local name: {1} {2}".format(
                            table, local_id, metadata_map[metadata_key][table]['local_id']))

    return None

if __name__ == "__main__":
    main()

