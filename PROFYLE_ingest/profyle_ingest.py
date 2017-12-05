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
    dataset = Dataset('PROFYLE')
    dataset.setDescription('PROFYLE METADATA TEST')
    # Open and load the data
    with GA4GHRepo(repo_filename) as repo:
        # Add dataset
        repo.add_dataset(dataset)
        # Iterate threough all people and add their data info the dataset
        for patient in metadata['profyle']:
            patient_id = patient["individual"]["patient_id"]
            # Individual
            individual = Individual(dataset, localId=patient_id)
            individual_object = individual.populateFromJson(
                json.dumps(patient["individual"]))
            # Biosample
            biosample = Biosample(dataset, localId=patient_id)
            biosample_object = biosample.populateFromJson(
                json.dumps(patient["biosample"]))
            biosample_object._individual_id = individual_object.getId()
            # Experiment
            experiment = Experiment(dataset, localId=patient_id)
            experiment_object = experiment.populateFromJson(
                json.dumps(patient["experiment"]))
            experiment_object._biosample_id = biosample_object.getId()
            # Analysis            
            analysis = Analysis(dataset, localId=patient_id)
            analysis_object = analysis.populateFromJson(
                json.dumps(patient["analysis"]))
            analysis_object._experiment_id = experiment_object.getId()
            # Add object into the repo file
            repo.add_individual(individual_object)
            repo.add_biosample(biosample_object)
            repo.add_experiment(experiment_object)
            repo.add_analysis(analysis_object)
    return None

if __name__ == "__main__":
    main()

