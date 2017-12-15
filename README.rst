==============
PROFYLEingest
==============


.. image:: https://img.shields.io/travis/CanDIG/PROFYLE_ingest.svg
        :target: https://travis-ci.org/CanDIG/PROFYLE_ingest

.. image:: https://pyup.io/repos/github/CanDIG/PROFYLE_ingest/shield.svg
     :target: https://pyup.io/repos/github/CanDIG/PROFYLE_ingest/
     :alt: Updates


Routines for ingesting PROFYLE metadata into a GA4GH Reads & Variants server
for powering a dashboard.  Requires `ga4gh-server
<https://github.com/ga4gh/ga4gh-server>`_
and `docopt
<http://docopt.readthedocs.io/en/latest/>`_.

* Free software: GNU General Public License v3

TODO:

- update existing repo rather than overwriting
- make use of existing jsonschema for validation/object creation

You can run the ingestion and test a server with the resulting repo as follows (requires Python 2.7
for the ga4gh reads/variants server:)

.. code:: bash

    # Install
    virtualenv profyle_test
    cd profyle_test
    source bin/activate
    pip install --upgrade pip
    pip install -U setuptools
    pip install git+https://github.com/CanDIG/ga4gh-schemas.git@profyle#egg=ga4gh_schemas
    pip install git+https://github.com/CanDIG/ga4gh-client.git@profyle#egg=ga4gh_client
    pip install git+https://github.com/CanDIG/ga4gh-server.git@profyle#egg=ga4gh_server
    pip install git+https://github.com/CanDIG/PROFYLE_ingest.git@profyle#egg=PROFYLE_ingest

    # setup initial peers
    mkdir -p ga4gh/server/templates
    touch ga4gh/server/templates/initial_peers.txt

    # ingest profyle data and make the repo
    mkdir ga4gh-example-data
    PROFYLE_ingest ga4gh-example-data/registry.db <path to example profake data, like: profake_test.json>

    # optional
    # add peer site addresses
    ga4gh_repo add-peer ga4gh-example-data/registry.db <peer site IP address, like: http://127.0.0.1:8001>

    # optional
    # create dataset for reads and variants
    ga4gh_repo add-dataset --description "Reads and variants dataset" ga4gh-example-data/registry.db read_and_variats_dataset

    # optinal
    # add reference set, data source: https://www.ncbi.nlm.nih.gov/grc/human/ or http://genome.wustl.edu/pub/reference/
    ga4gh_repo add-referenceset ga4gh-example-data/registry.db <path to downloaded reference set, like GRCh37-lite.fa> -d "GRCh37-lite human reference genome" --name GRCh37-lite --sourceUri "http://genome.wustl.edu/pub/reference/GRCh37-lite/GRCh37-lite.fa.gz"

    # optional
    # add reads
    ga4gh_repo add-readgroupset -r -I <path to bam index file> -R GRCh37-lite ga4gh-example-data/registry.db read_and_variats_dataset <path to bam file>

    # optional
    # add variants
    ga4gh_repo add-variantset -I <path to variants index file> -R GRCh37-lite ga4gh-example-data/registry.db read_and_variats_dataset <path to vcf file>
    
    # optional
    # add sequence ontology set
    # wget https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/so.obo
    ga4gh_repo add-ontology ga4gh-example-data/registry.db <path to sequence ontology set, like: so.obo> -n so-xp

    # optional
    # add features/annotations
    #
    ## get the following scripts
    # https://github.com/ga4gh/ga4gh-server/blob/master/scripts/glue.py
    # https://github.com/ga4gh/ga4gh-server/blob/master/scripts/generate_gff3_db.py
    #
    ## download the relevant annotation release from Gencode
    # https://www.gencodegenes.org/releases/current.html
    #
    ## decompress
    # gunzip gencode.v27.annotation.gff3.gz
    #
    ## buid the annotation database
    # python generate_gff3_db.py -i gencode.v27.annotation.gff3 -o gencode.v27.annotation.db -v    
    #
    # add featureset
    ga4gh_repo add-featureset ga4gh-example-data/registry.db read_and_variats_dataset <path to the annotation.db> -R GRCh37-lite -O so-xp

    # optional
    # add phenotype association set from Monarch Initiative
    # wget http://nif-crawler.neuinfo.org/monarch/ttl/cgd.ttl
    ga4gh_repo add-phenotypeassociationset ga4gh-example-data/registry.db read_and_variats_dataset <path to the folder containing cdg.ttl>

    # optional
    # add disease ontology set, like: NCIT
    # wget http://purl.obolibrary.org/obo/ncit.obo
    ga4gh_repo add-ontology -n NCIT ga4gh-example-data/registry.db ncit.obo

    # launch the server
    # at different IP and/or port: ga4gh_server --host 127.0.0.1 --port 8000
    ga4gh_server


and then, from a web browser:

    https://127.0.0.1:8000/candig


and then, from another terminal:

.. code:: bash

    curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
        http://127.0.0.1:8000/datasets/search \
        | jq '.'

giving:

.. code:: JSON

    {
      "datasets": [
        {
          "description": "PROFYLE test metadata",
          "id": "WyJQUk9GWUxFIl0",
          "name": "PROFYLE"
        }
      ]
    }

One can search for individuals within that dataset:

.. code:: bash

    curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
        -d '{ "datasetId": "WyJQUk9GWUxFIl0" }' http://127.0.0.1:8000/individuals/search \
        | jq '.individuals[] | {ga4ghid: .id, profyleid: .name}'

.. code:: JSON

    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAwMUEiXQ",
      "profyleid": "PRO-00001A"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAwMkIiXQ",
      "profyleid": "PRO-00002B"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAwM0MiXQ",
      "profyleid": "PRO-00003C"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAxMk4iXQ",
      "profyleid": "PRO-00012N"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAxM1AiXQ",
      "profyleid": "PRO-00013P"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAxNVMiXQ",
      "profyleid": "PRO-00015S"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAxNlQiXQ",
      "profyleid": "PRO-00016T"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAxN1UiXQ",
      "profyleid": "PRO-00017U"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDAxOVciXQ",
      "profyleid": "PRO-00019W"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDBCQzEiXQ",
      "profyleid": "PRO-000BC1"
    }
    {
      "ga4ghid": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDBCQzIiXQ",
      "profyleid": "PRO-000BC2"
    }

get the data for a specific individual:

.. code:: bash

    curl -X GET --header 'Content-Type: application/json' --header 'Accept: application/json' \
        http://127.0.0.1:8000/individuals/WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDBCQzEiXQ | jq '.'


list biosamples.:

.. code:: bash

    curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
        -d '{ "datasetId": "WyJQUk9GWUxFIl0" }' http://127.0.0.1:8000/biosamples/search \
        | jq '.biosamples[] | {name: .name, individual_ga4gh_id: .individualId}'

or experiments:

.. code:: bash

     curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
        -d '{ "datasetId": "WyJQUk9GWUxFIl0" }' http://127.0.0.1:8000/experiments/search \
        | jq '.experiments[] | { name: .name, molecule: .molecule, sequencingCenter: .sequencingCenter }'
