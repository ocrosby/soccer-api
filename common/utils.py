import pprint
import requests

from bs4 import BeautifulSoup

from common import config
from common.extensions import cache

import lib.topdrawer as topdrawer

def get_conference_name_from_cell(cell):
    strong_tags = cell.find_all("strong")

    for strong_tag in strong_tags:
        text = strong_tag.text.strip()

        if len(text) > 0:
            text = text.upper()
            text = text.replace("CONFERENCE", "")
            text = text.strip()
            return text

    return None


def get_state_from_item(item):
    if item is None:
        return None

    text = item.text.strip()

    if "(" in text and ")" in text:
        state = text[text.find("(")+1:text.find(")")]
        state = state.strip()
        return state

    return None


def get_clubs_from_cell(cell):
    clubs = []

    outer_list = cell.find("ul")
    inner_list = outer_list.find("ul")
    items = inner_list.find_all("li")

    for item in items:
        anchor = item.find("a")
        club = {"name": anchor.text.strip(), "state": get_state_from_item(
            item), "conference": get_conference_name_from_cell(cell), "url": anchor["href"]}
        club["name"] = club["name"].replace("  ", " ")

        clubs.append(club)

    return clubs


class ClubSearch:
    def __init__(self):
        """Constructor"""
        self.ga_clubs = None
        self.ecnl_clubs = None

    # @cache.cached(timeout=604800)
    def get_ga_clubs(self):
        return config.GA_CLUBS

    @cache.cached(timeout=604800)
    def get_ecnl_clubs(self):
        if self.ecnl_clubs is not None:
            return self.ecnl_clubs

        url = "https://public.totalglobalsports.com/api/Event/get-org-club-list-by-orgID/9"

        response = requests.get(url)

        response.raise_for_status()

        json_response = response.json()

        clubs = []

        for item in json_response["data"]:
            club = {}

            club["id"] = item["clubID"]
            club["orgId"] = item["orgID"]
            club["name"] = item["clubFullName"].strip()
            club["city"] = item["city"].strip()
            club["state"] = item["stateCode"].strip()
            club["logo"] = item["clubLogo"].strip()

            club["name"] = club["name"].replace("  ", " ")

            clubs.append(club)

        self.ecnl_clubs = clubs

        return clubs

class TopDrawerSoccer:
    def __init__(self):
        """Constructor"""
        self.prefix = "https://www.topdrawersoccer.com"

    @cache.memoize(timeout=604800)
    def get_conference(self, gender: str, division: str, name: str):
        conferences = self.get_conferences(gender, division)

        for conference in conferences:
            if conference['name'] == name:
                return conference

        return None

    @cache.memoize(timeout=604800)
    def get_conferences(self, gender: str, division: str):
        url = "https://www.topdrawersoccer.com/college-soccer/college-conferences"

        suffix = ""
        if division in config.DIVISION_MAPPING:
            suffix = config.DIVISION_MAPPING[division]

        response = requests.get(url + suffix)

        response.raise_for_status()

        conferences = []

        soup = BeautifulSoup(response.content, "html.parser")

        column_elements = soup.find_all("div", class_="col-lg-6")

        for column_element in column_elements:
            heading_element = column_element.find("div", class_="heading-rectangle")
            heading = heading_element.text.strip()

            table = column_element.find("table", class_=["table_striped", "tds_table"])

            if table is None:
                continue

            cells = table.find_all("td")

            for cell in cells:
                url = "https://www.topdrawersoccer.com" + cell.find("a")["href"]
                name = cell.text.strip()

                conference_id = int(url.split('/')[-1].split('-')[-1])

                schools = None

                if gender == "male" and "Men's" in heading:
                    conferences.append(
                        {"id": conference_id, "name": name, "url": url, "schools": schools})

                if gender == "female" and "Women's" in heading:
                    conferences.append(
                        {"id": conference_id, "name": name, "url": url, "schools": schools})

        return conferences
