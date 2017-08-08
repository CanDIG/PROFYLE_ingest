#!/usr/bin/env python
"""create_repo - creates a GA4GH repo representing PROFYLE metadata entries.
Currently only creates individuals, and overwrites existing repo if it exists.

TODO:
    ingest biosamples
    ingest experiments/analyses
    update existing repo rather than overwriting
    make use of the jsonschema for the input data

Usage:
  create_repo.py <repo_filename> <profyle_dir>

Options:
  -h --help        Show this screen
  -v --version     Version
  <repo_filename>  Path/filename of ga4gh reads/variants repository to create
  <profyle_dir>    Root directory to crawl to ingest PROFYLE metadata
"""

from __future__ import print_function
from docopt import docopt
import json
import datetime
import os
import glob
import ga4gh.server.datarepo as repo
import ga4gh.server.datamodel.datasets as datasets
import ga4gh.server.datamodel.bio_metadata as biodata

_male = '"sex": {"term_id":"PATO:00200000", "term":"male genotypic sex"}'
_female = '"sex": {"term_id":"PATO:00200000", "term":"female genotypic sex"}'
_human = '"species": {"term_id":"NCBITaxon:9606", "term":"Homo sapiens"}'


class AttributesList(object):
    """
    A convenience class for building GA4GH Attributes messages
    as dictionaries.

    The Attributes message is a map from string to AttributeValueList
    (eg, key-value), where the value looks like:
      "values": [value_type, value, value...]
    (eg, can be repeating with multiple value)
    and value_type is the name of the type.

    An Attribute list can contain other attribute lists.

    See:
    https://github.com/ga4gh/ga4gh-schemas/blob/master/src/main/proto/ga4gh/common.proto#L191-L215
    """
    def __init__(self):
        self._dict = {}

    def _attrtype(self, value):
        typenames = {int: 'int64_value', bool: 'bool_value',
                     float: 'double_value', str: 'string_value'}
        if isinstance(value, AttributesList):
            return "attributes"
        if type(value) in typenames:
            return typenames[type(value)]
        return 'string_value'

    def add(self, name, value):
        if value is None:   # don't add empty fields
            return
        if isinstance(value, AttributesList):
            self._dict[name] = value.as_dict()
        else:
            self._dict[name] = value

    def add_from_dict(self, d, name):
        if name not in d:
            return
        if d[name] is None:
            return
        self.add(name, d[name])

    def as_dict(self):
        return self._dict

    def __str__(self):
        return(str(self._dict))


class GA4GHIndividual(object):
    """
    First pass at mapping a PROFYLE individual to a GA4GH individual.
    Currently this involves stuffing a lot of data into Attributes
    (a generic key-value field).  The convention by which this is
    done needs to be agreed upon - this is just a first pass.
    """
    def __init__(self, dataset, profyle_individual):
        globalid = profyle_individual['profyle_national_id']
        self.individual = biodata.Individual(dataset, globalid)
        self.individual.populateFromJson('{' + _human + '}')

        if 'sex' in profyle_individual:
            if profyle_individual['sex'] in ["Male", "male"]:
                self.individual.populateFromJson('{' + _male + '}')
            elif profyle_individual['sex'] in ["Female", "female"]:
                self.individual.populateFromJson('{' + _female + '}')

        self.attrs = AttributesList()
        self.attrs.add_from_dict(profyle_individual, 'ethnicity')
        self.attrs.add_from_dict(profyle_individual, 'disease')
        self.attrs.add_from_dict(profyle_individual, 'age')
        self.attrs.add_from_dict(profyle_individual, 'profyle_regional_id')
        self.attrs.add_from_dict(profyle_individual, 'internal_id')

        team = AttributesList()
        profyle_rec_team = profyle_individual['recruitement_team']

        team.add_from_dict(profyle_rec_team, "group_name")
        team.add_from_dict(profyle_rec_team, "hospital")
        team.add_from_dict(profyle_rec_team, "province")
        self.attrs.add('recruitment_team', team)

        self.individual.setAttributes(self.attrs.as_dict())

    def get_individual(self):
        return self.individual

    def get_attributes(self):
        return self.attrs

    def __str__(self):
        return str(self.individual.toProtocolElement())


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

    def add_individual(self, ga4gh_individual):
        person = ga4gh_individual.get_individual()
        self._repo.insertIndividual(person)
        self._repo.commit()
        self._repo.verify()

    def add_sample(self, biosample):
        self._repo.insertBiosample(biosample)
        self._repo.commit()
        self._repo.verify()

    def add_dataset(self, dataset):
        self._repo.insertDataset(dataset)
        self._repo.commit()
        self._repo.verify()


def GA4GHBiosamples(dataset, ga4gh_individual, profyle_individual):
    """
    Takes sample information from a PROFYLE and creates a list of
    GA4GH Biosample messages from it.
    """
    now = datetime.date.today()
    nowstr = now.isoformat()
    ga4gh_individual_id = ga4gh_individual.get_individual().getId()

    biosamplelist = []
    for sample_name in profyle_individual['sample']:
        sample = profyle_individual['sample'][sample_name]
        biosample = biodata.Biosample(dataset, sample_name)

        biosampledict = {"created": nowstr, "updated": nowstr}
        biosampledict["individual_id"] = ga4gh_individual_id
        biosampledict["description"] = sample["remarks"]

        # not 100% sure I'm doing handling the disease Ontology Term correctly
        disease = {"term_id": profyle_individual["disease_ontology_uri"],
                   "term": profyle_individual["disease"]}
        biosampledict["disease"] = disease

        biosample.populateFromJson(json.dumps(biosampledict))

        # put tissue type in attributes (biosample does not have tissuetype?)
        # as well as tumour yes/no and storage location
        attrs = AttributesList()
        attrs.add_from_dict(sample, 'tissue_type')
        attrs.add_from_dict(sample, 'tissue_type_ontology_url')
        attrs.add_from_dict(sample, 'tumour')
        attrs.add_from_dict(sample, 'storage_location')
        biosample.setAttributes(attrs.as_dict())
        biosamplelist.append(biosample)

    return biosamplelist


def main():
    args = docopt(__doc__, version='create_repo 0.1')
    repo_filename, profyle_dir = args['<repo_filename>'], args['<profyle_dir>']

    dataset = datasets.Dataset("PROFYLE")
    dataset.setDescription("PROFYLE test metadata")

    with GA4GHRepo(repo_filename) as repo:
        repo.add_dataset(dataset)

        donor_dirs = glob.glob(profyle_dir + '/*')
        for donor_dir in donor_dirs:
            if not os.path.isdir(donor_dir):
                continue
            donor_name = os.path.basename(donor_dir)
            print(donor_name)
            donor_file = os.path.join(donor_dir, donor_name+'.json')

            profyle_individual = json.loads(open(donor_file).read())
            person = GA4GHIndividual(dataset, profyle_individual)
            repo.add_individual(person)

            samples = GA4GHBiosamples(dataset, person, profyle_individual)
            for sample in samples:
                repo.add_sample(sample)


if __name__ == "__main__":
    main()
