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

- ingest experiments/analyses
- update existing repo rather than overwriting
- make use of existing jsonschema for validation/object creation

You can run the ingestion and test a server with the resulting repo as follows (requires Python 2.7
for the ga4gh reads/variants server:)

.. code:: bash

    # Install
    virtualenv pitest
    cd pitest
    source bin/activate
    pip install git+https://github.com/CanDIG/ga4gh-schemas.git@master#egg=ga4gh_schemas
    pip install git+https://github.com/CanDIG/ga4gh-client.git@master#egg=ga4gh_client
    pip install git+https://github.com/CanDIG/ga4gh-server.git@master#egg=ga4gh_server
    pip install git+https://github.com/CanDIG/PROFYLE_ingest.git

    # work around peers issue
    mkdir -p ga4gh/server/templates/
    touch ga4gh/server/templates/initial_peers.txt
    
    # make the repo
    mkdir ga4gh-example-data
    PROFYLE_ingest ga4gh-example-data/registry.db /path/to/PROFYLE_metadata/root_folder_example/

    ga4gh_server


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
