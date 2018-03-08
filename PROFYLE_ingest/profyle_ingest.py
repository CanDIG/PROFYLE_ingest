#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
profyle_ingest.py - Creates a new ga4gh dataset and parses profyle metadata
information into it. It populates Individual, Biosample, Experiment and
Analysis objects.

Usage:
  profyle_ingest.py <repo_filename> <metadata_json>

Options:
  -h --help        Show this screen
  -v --version     Version
  <repo_filename>  Path and filename of the ga4gh repository
  <metadata_json>  Path and filename information to the profyle metadata json file.

"""

import json
import os
from docopt import docopt

import ga4gh.server.datarepo as repo

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
from ga4gh.server.datamodel.bio_metadata import Experiment
from ga4gh.server.datamodel.bio_metadata import Analysis


class GA4GHRepo(object):
    def __init__(self, filename):
        self._filename = filename
        self._repo = None

    def __enter__(self):
        if os.path.isfile(self._filename):
            os.remove(self._filename)

        self._repo = repo.SqlDataRepository(self._filename)
        self._repo.open(repo.MODE_WRITE)
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

def main():
    """
    """
    # Parse arguments
    args = docopt(__doc__, version='profyle ingest 0.1')
    # Handle the passed arguments
    repo_filename = args['<repo_filename>']
    metadata_json = args['<metadata_json>']
    # Read and parse profyle metadata json
    with open(metadata_json, 'r') as json_datafile:
        metadata = json.load(json_datafile, 'UTF-8')
    # Create a dataset
    dataset = Dataset('METADATA')
    dataset.setDescription('METADATA TEST SERVER')
    # Open and load the data
    with GA4GHRepo(repo_filename) as repo:
        # Add dataset
        repo.add_dataset(dataset)
        # Iterate through all people and add their data info the dataset
        for individual in metadata['metadata']:
            # patient_id
            patient_id = individual["Patient"]["patientId"]

            # Patient
            patient = Patient(dataset, localId=patient_id)
            patient_object = patient.populateFromJson(
                json.dumps(individual["Patient"]))
            # Add object into the repo file
            repo.add_patient(patient_object)

            # Enrollment
            enrollment = Enrollment(dataset, localId=patient_id)
            enrollment_object = enrollment.populateFromJson(
                json.dumps(individual["Enrollment"]))
            # Add object into the repo file
            repo.add_enrollment(enrollment_object)

            # Consent
            consent = Consent(dataset, localId=patient_id)
            consent_object = consent.populateFromJson(
                json.dumps(individual["Consent"]))
            # Add object into the repo file
            repo.add_consent(consent_object)

            # Diagnosis
            diagnosis = Diagnosis(dataset, localId=patient_id)
            diagnosis_object = diagnosis.populateFromJson(
                json.dumps(individual["Diagnosis"]))
            # Add object into the repo file
            repo.add_diagnosis(diagnosis_object)

            # Sample
            sample = Sample(dataset, localId=patient_id)
            sample_object = sample.populateFromJson(
                json.dumps(individual["Sample"]))
            # Add object into the repo file
            repo.add_sample(sample_object)

            # Treatment
            treatment = Treatment(dataset, localId=patient_id)
            treatment_object = treatment.populateFromJson(
                json.dumps(individual["Treatment"]))
            # Add object into the repo file
            repo.add_treatment(treatment_object)

            # Outcome
            outcome = Outcome(dataset, localId=patient_id)
            outcome_object = outcome.populateFromJson(
                json.dumps(individual["Outcome"]))
            # Add object into the repo file
            repo.add_outcome(outcome_object)

            # Complication
            complication = Complication(dataset, localId=patient_id)
            complication_object = complication.populateFromJson(
                json.dumps(individual["Complication"]))
            # Add object into the repo file
            repo.add_complication(complication_object)

            # Tumourboard
            tumourboard = Tumourboard(dataset, localId=patient_id)
            tumourboard_object = tumourboard.populateFromJson(
                json.dumps(individual["Tumourboard"]))
            # Add object into the repo file
            repo.add_tumourboard(tumourboard_object)


#        # Iterate through all people and add their data info the dataset
#        for patient in metadata['profyle']:
#
#            patient_id = patient["individual"]["patient_id"]
#
#            # Individual
#            individual = Individual(dataset, localId=patient_id)
#            individual_object = individual.populateFromJson(
#                json.dumps(patient["individual"]))
#            # Biosample
#            biosample = Biosample(dataset, localId=patient_id)
#            biosample_object = biosample.populateFromJson(
#                json.dumps(patient["biosample"]))
#            biosample_object._individual_id = individual_object.getId()
#            # Experiment
#            experiment = Experiment(dataset, localId=patient_id)
#            experiment_object = experiment.populateFromJson(
#                json.dumps(patient["experiment"]))
#            experiment_object._biosample_id = biosample_object.getId()
#            # Analysis
#            analysis = Analysis(dataset, localId=patient_id)
#            analysis_object = analysis.populateFromJson(
#                json.dumps(patient["analysis"]))
#            analysis_object._experiment_id = experiment_object.getId()
#            # Add object into the repo file
#            repo.add_individual(individual_object)
#            repo.add_biosample(biosample_object)
#            repo.add_experiment(experiment_object)
#            repo.add_analysis(analysis_object)
    return None

if __name__ == "__main__":
    main()

