import requests

from bs4 import BeautifulSoup

from common.extensions import cache
from common import config
from lib import topdrawer

from . import ga
from . import ecnl

division_mapping = {
    "di": "/di/divisionid-1",
    "dii": "/dii/divisionid-2",
    "diii": "/diii/divisionid-3",
    "naia": "/naia/divisionid-4",
    "njcaa": "/njcaa/divisionid-5"
}

PREFIX = "https://www.topdrawersoccer.com"


@cache.memoize(timeout=604800)
def get_conferences_content(division: str):
    """Returns the HTML from the college conferences page."""
    url = "https://www.topdrawersoccer.com/college-soccer/college-conferences"

    suffix = ""

    if division in division_mapping:
        suffix = division_mapping[division]

    url = url + suffix
    response = requests.get(url)

    response.raise_for_status()

    return response.content


@cache.memoize(timeout=604800)
def get_conference_commitments_content(gender: str, division: str, conference_name: str):
    """Returns the HTML from the given conferences commitments page."""
    conference = get_conference(gender, division, conference_name)
    url = conference["url"] + "/tab-commitments"

    response = requests.get(url)

    response.raise_for_status()

    return response.content


@cache.memoize(timeout=604800)
def get_conferences(gender: str, division: str):
    """Return a list of all conferences."""
    conferences = []

    content = get_conferences_content(division)
    soup = BeautifulSoup(content, "html.parser")
    columns = soup.find_all("div", class_=["col-lg-6"])

    for column in columns:
        heading = column.find("div", class_=["heading-rectangle"]).text.strip()

        if gender == "male" and "Men's" not in heading:
            continue

        if gender == "female" and "Women's" not in heading:
            continue

        table = column.find("table", class_=["table_stripped", "tds_table"])
        cells = table.find_all("td")

        for cell in cells:
            url = PREFIX + cell.find("a")["href"]
            conferences.append({
                "id": int(url.split('/')[-1].split('-')[-1]),
                "name": cell.text.strip(),
                "url": url
            })

    return conferences


@cache.memoize(timeout=604800)
def get_conference(gender: str, division: str, conference_name: str):
    """Return a conference by name."""
    conferences = get_conferences(gender, division)

    for conference in conferences:
        if conference["name"] == conference_name:
            return conference

    return None

@cache.memoize(timeout=604800)
def _is_ecnl_club(target_club_name, ecnl_clubs):
    if target_club_name is None:
        return False

    if ecnl_clubs is None:
        return False

    temp = target_club_name.strip().lower()

    if len(temp) == 0:
        return False

    for club in ecnl_clubs:
        current_club_name = club["name"].strip().lower()

        if current_club_name == temp:
            return True

    return False


@cache.memoize(timeout=604800)
def _is_ga_club(target_club_name, ga_clubs):
    if target_club_name is None:
        return False

    if ga_clubs is None:
        return False

    temp = target_club_name.strip().lower()

    if len(temp) == 0:
        return False

    for club in ga_clubs:
        current_club_name = club["name"].strip().lower()

        if current_club_name == temp:
            return True

    return False

@cache.memoize(timeout=604800)  # 1 week
def _get_league(club_name: str, ecnl_clubs, ga_clubs):
    if club_name is None:
        return "Other"

    if len(club_name) == 0:
        return "Other"

    if _is_ecnl_club(club_name, ecnl_clubs):
        return "ECNL"
    elif _is_ga_club(club_name, ga_clubs):
        return "GA"
    else:
        print("Could not find the club (" + club_name + ")")
        return "Other"

@cache.memoize(timeout=604800)  # 1 week
def get_conference_commits(gender: str, division: str, conference_name: str, year: int):
    content = get_conference_commitments_content(gender, division, conference_name)

    soup = BeautifulSoup(content, "html.parser")
    tables = soup.find_all("table", class_=["table-striped", "tds-table", "female"])

    body = None
    for table in tables:
        header = table.find("thead", class_="female")
        if header is not None:
            body = table.find("tbody")

    if body is None:
        return []

    ecnl_clubs = ecnl.get_clubs()
    ga_clubs = ga.get_clubs()

    schools = []
    rows = body.find_all("tr")
    for row in rows:
        columns = row.find_all("td")
        if len(columns) == 1:
            school = {
                "name": columns[0].text.strip(),
                "players": []
            }
            schools.append(school)
        else:
            grad_year = columns[1].text.strip()

            if int(grad_year) == year:
                player = {
                    "name": columns[0].text.strip(),
                    "url": PREFIX + columns[0].find("a")["href"],
                    "year": grad_year,
                    "position": columns[2].text.strip(),
                    "city": columns[3].text.strip(),
                    "state": columns[4].text.strip(),
                    "club": columns[5].text.strip().replace("  ", " ")
                }

                topdrawer.load_player_details(player)

                player["club"] = config.translate_club_name(player["club"])
                player["league"] = _get_league(player["club"], ecnl_clubs, ga_clubs)

                school["players"].append(player)

    return schools


def _get_player_rating(element):
    span = element.find("span", class_=["rating"])

    if span is None:
        return None

    rating = span["style"]
    rating = int(rating.split(':')[-1].split('%')[0]) // 20

    if rating > 0:
        rating = str(rating) + ' star'
    else:
        rating = "Not Rated"

    return rating


def _get_player_position(element):
    div = element.find("div", class_=["player-position"])

    if div is None:
        return None

    buffer = div.text.strip()
    tokens = buffer.split("-")
    position = tokens[0].strip()

    return position


def _get_player_commitment(element):
    div = element.find("div", class_=["player-position"])
    if div is None:
        return None

    anchor = div.find('a')
    if anchor is None:
        return None

    commitment = anchor.text
    commitment = commitment.strip()

    return commitment


def _get_player_commitment_url(element):
    div = element.find("div", class_=["player-position"])
    if div is None:
        return None

    anchor = div.find('a')
    if anchor is None:
        return None

    url = anchor["href"]
    url = url.strip()
    url = PREFIX + url

    return url


def _load_profile_grid_settings(element, details):
    container = element.find("ul", class_=["profile_grid"])
    items = container.findChildren("li")

    for item in items:
        lvalue, rvalue = item.text.strip().split(":")

        lvalue = lvalue.strip()
        rvalue = rvalue.strip()

        if lvalue == "Club":
            details["club"] = rvalue
        elif lvalue == "Team Name":
            details["team"] = rvalue
        elif lvalue == "Jersey Number":
            details["jerseyNumber"] = rvalue
        elif lvalue == "High School":
            details["highSchool"] = rvalue
        elif lvalue == "Region":
            details["region"] = rvalue
        else:
            print("Unknown lvalue " + lvalue + " on player detail page.")


@cache.memoize(timeout=86400)  # 1 day
def load_player_details(player):
    if player is None:
        return

    if "url" not in player:
        return

    response = requests.get(player["url"])

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    _load_profile_grid_settings(soup, player)

    player["rating"] = _get_player_rating(soup)
    player["position"] = _get_player_position(soup)
    player["commitment"] = _get_player_commitment(soup)
    player["commitmentUrl"] = _get_player_commitment_url(soup)
