# PROFYLE_ingest

Routines for ingesting PROFYLE metadata into a GA4GH Reads & Variants server
for powering a dashboard.  Requires [ga4gh-server](https://github.com/ga4gh/ga4gh-server)
and [docopt](http://docopt.readthedocs.io/en/latest/).

TODO:
- ingest biosamples
- ingest experiments/analyses
- update existing repo rather than overwriting

You can run the ingestion and test a server with the resulting repo as follows:

```bash
# make the repo
$ mkdir ga4gh-example-data
$ ./create_repo.py ga4gh-example-data/registry.db /path/to/PROFYLE_metadata/root_folder_example/

# fix for odd ga4gh server config
$ mkdir -p ga4gh/server/templates
$ touch ga4gh/server/templates/initial_peers.txt
$ ga4gh-server
```

and then, from another terminal:

```bash
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
    http://127.0.0.1:8000/datasets/search \
    | jq '.'
```
```JSON
{
  "datasets": [
    {
      "description": "PROFYLE test metadata",
      "id": "WyJQUk9GWUxFIl0",
      "name": "PROFYLE"
    }
  ]
}
```
```bash
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
    -d '{ "datasetId": "WyJQUk9GWUxFIl0" }' http://127.0.0.1:8000/individuals/search \
    | jq '.individuals[] | {ga4ghid: .id, profyleid: .name}'
```
```JSON
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
```
```bash
curl -X GET --header 'Content-Type: application/json' --header 'Accept: application/json' \
    http://127.0.0.1:8000/individuals/WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDBCQzEiXQ | jq '.'
```
```JSON
{
  "species": {
    "term": "Homo sapiens",
    "termId": "NCBITaxon:9606"
  },
  "attributes": {
    "attr": {
      "internal_id": {
        "values": [
          {
            "stringValue": "POG669"
          }
        ]
      },
      "recruitment_team": {
        "values": [
          {
            "attributes": {
              "attr": {
                "province": {
                  "values": [
                    {
                      "stringValue": "British Columbia"
                    }
                  ]
                }
              }
            }
          },
          {
            "attributes": {
              "attr": {
                "hospital": {
                  "values": [
                    {
                      "stringValue": "BC cancer agency"
                    }
                  ]
                }
              }
            }
          }
        ]
      }
    }
  },
  "id": "WyJQUk9GWUxFIiwiaSIsIlBSTy0wMDBCQzEiXQ",
  "datasetId": "WyJQUk9GWUxFIl0",
  "name": "PRO-000BC1"
}
```
