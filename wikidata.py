import requests
import urllib
from . import logging
from .files import write_force
from .files import read
import pandas
import json


def query_to_json(query, path):
    endpoint_url = "https://query.wikidata.org/sparql"
    args = urllib.parse.urlencode({
        'query': query,
        'format': 'json'
    })
    r = requests.get(f"{endpoint_url}?{args}", timeout=3600)
    logging.info(f"CODE: {r.status_code}")
    write_force(path, r.text)


def json_to_tsv_clean(path_in, path_out):
    content = read(path_in)
    data = json.loads(content)
    columns = data['head']['vars']
    data_2 = []
    for x in data['results']['bindings']:
        e = {}
        for i, y in enumerate(x.values()):
            e[columns[i]] = y['value'].replace("http://www.wikidata.org/entity/", "")
        data_2.append(e)
    df = pandas.DataFrame(data_2).drop_duplicates()
    df.to_csv(path_out, index=False, sep="\t")
