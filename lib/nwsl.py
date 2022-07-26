import requests

from bs4 import BeautifulSoup
from common.extensions import cache

@cache.cached(timeout=604800, key_prefix='nwsl_standings')
def get_standings():
    url = "https://d2nkt8hgeld8zj.cloudfront.net/services/nwsl.ashx/standings"

    response = requests.get(url)
    response.raise_for_status()

    json = response.json()

    return json["data"]["divisions"][0]["rankings"]

@cache.cached(timeout=604800, key_prefix='nwsl_players')
def get_players():
    url = "https://d2nkt8hgeld8zj.cloudfront.net/services/nwsl.ashx/players"

    response = requests.get(url)
    response.raise_for_status()

    json = response.json()

    results = []

    for record in json["data"]:
        if record['team'] is not None:
            results.append(record)

    return results
