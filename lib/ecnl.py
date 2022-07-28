import requests

from bs4 import BeautifulSoup

from common.utils import cache

def get_clubs():
    url = "https://public.totalglobalsports.com/api/Event/get-org-club-list-by-orgID/9"

    response = requests.get(url)
    response.raise_for_status()
    json_response = response.json()

    clubs = []
    for item in json_response["data"]:
        club = {
            "id": item["clubID"],
            "orgId": item["orgID"],
            "name": item["clubFullName"].strip().replace("  ", " "),
            "city": item["city"].strip(),
            "state": item["stateCode"].strip(),
            "logo": item["clubLogo"].strip(),
        }

        clubs.append(club)

    return clubs
