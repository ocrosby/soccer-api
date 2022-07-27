import requests

from bs4 import BeautifulSoup

from common.extensions import cache
from common import tools
from common import config
from lib import topdrawer

from . import ga
from . import ecnl

PREFIX = "https://www.topdrawersoccer.com"


def get_identifier_from_url(url):
    if url is None:
        return None

    url = url.strip()
    if len(url) == 0:
        return None

    tokens = url.split('/')
    last_segment = tokens[-1]

    tokens = last_segment.split('-')
    buffer = tokens[-1]
    identifier = int(buffer)

    return identifier

@cache.memoize(timeout=604800)
def get_conferences_content(division: str):
    """Returns the HTML from the college conferences page."""
    url = "https://www.topdrawersoccer.com/college-soccer/college-conferences"

    suffix = ""

    if division in config.DIVISION_MAPPING:
        suffix = config.DIVISION_MAPPING[division]

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


@cache.memoize(timeout=604800)  # 1 week
def _get_league(club_name: str, ecnl_clubs, ga_clubs):
    if club_name is None:
        return "Other"

    if len(club_name) == 0:
        return "Other"

    if tools.is_member_club(club_name, ecnl_clubs):
        return "ECNL"
    elif tools.is_member_club(club_name, ga_clubs):
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
            # print(f"Adding school {school['name']} ...")
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

                # print(f"Loading details for player '{player['name']}' ...")
                topdrawer.load_player_details(player)
                # print("Details loaded successfully")

                player["club"] = config.translate_club_name(player["club"])
                player["league"] = _get_league(player["club"], ecnl_clubs, ga_clubs)

                # print(f"Adding '{player['name']}' to '{school['name']}' ...")
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

    if container is None:
        return

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


def _get_transfer_position(cell):
    caption = cell.text.strip()
    if caption == "Player":
        return None

    if "\xa0" in caption:
        return caption.split("\xa0")[0].strip()

    return caption.split(" ")[0].strip()


def _get_transfer_name(cell):
    caption = cell.text.strip()
    if caption == "Player":
        return None

    if "\xa0" in caption:
        return caption.split("\xa0")[1].strip()

    return " ".join(caption.split(" ")[1:]).strip()


def _get_transfer(row):
    try:
        cells = row.find_all("td")

        name = _get_transfer_name(cells[0])
        print(f"Processing '{name}'")

        if name is None or len(name) == 0:
            return None

        transfer = {
            "name": name,
            "position": None,
            "url": None,
            "formerSchoolName": None,
            "formerSchoolUrl": None,
            "newSchoolName": None,
            "newSchoolUrl": None
        }

        transfer["position"] = _get_transfer_position(cells[0])
        transfer["url"] = tools.get_anchor_url(cells[0], PREFIX)

        if len(cells) > 1:
            transfer["formerSchoolName"] = tools.get_anchor_text(cells[1])
            transfer["formerSchoolUrl"] = tools.get_anchor_url(cells[1], PREFIX)

        if len(cells) > 2:
            transfer["newSchoolName"] = tools.get_anchor_text(cells[2])
            transfer["newSchoolUrl"] = tools.get_anchor_url(cells[2], PREFIX)

    except Exception as err:
        print(row.text)
        print(err)

    print(transfer)

    return transfer


@cache.cached(timeout=86400, key_prefix='transfers')  # cache for 1 day
def get_transfers():
    url = "https://www.topdrawersoccer.com/college-soccer-articles/2022-womens-di-transfer-tracker_aid50187"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")

    transfers = []
    for row in rows:
        player = _get_transfer(row)
        if player is None:
            continue

        transfers.append(player)

    return transfers

@cache.memoize(timeout=604800) # 1 week
def get_conferences(gender: str, division: str):
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
            url = tools.get_anchor_url(cell, PREFIX)
            name = tools.get_anchor_text(cell)

            conference_id = get_identifier_from_url(url)

            if gender == "male" and "Men's" in heading:
                conferences.append(
                    {"id": conference_id, "name": name, "url": url})

            if gender == "female" and "Women's" in heading:
                conferences.append(
                    {"id": conference_id, "name": name, "url": url})

    return conferences

def _generate_player_suffix(gender: str, position: str, grad_year: str, region: str, state: str, page: int):
    suffix = "&genderId=" + gender
    suffix += "&positionId=" + str(position)
    suffix += "&graduationYear=" + grad_year
    suffix += "&regionId=" + str(region)
    suffix += "&countyId=" + str(state)
    suffix += "&pageNo=" + str(page)
    suffix += "&area=clubplayer&sortColumns=0&sortDirections=1&search=1"

    return suffix

def _get_search_pages(element):
    pagination = element.find("ul", class_=["pagination"])

    if pagination is None:
        return []

    page_items = pagination.findChildren("li", class_=["page-item"])

    pages = []
    for page_item in page_items:
        text = page_item.text.strip()

        if text in ["Previous", "1", "Next"]:
            continue

        pages.append(int(text))

    return pages

def _extract_club(item):
    buffer = item.find("div", class_="ml-2").text.strip()
    target = buffer.split('\t\t\t\t')[1].strip()
    pieces = target.split('/')

    if len(pieces) >= 1:
        return pieces[0]

    return None

def _extract_high_school(item):
    buffer = item.find("div", class_="ml-2").text.strip()
    target = buffer.split('\t\t\t\t')[1].strip()
    pieces = target.split('/')

    if len(pieces) == 1:
        high_school = None
    elif len(pieces) == 2:
        high_school = pieces[1]
    else:
        high_school = None

    return high_school

def _extract_image_url(item):
    image = item.find("img", class_="imageProfile")

    if image is not None:
        return PREFIX + image["src"]

    return None

def _extract_rating(item):
    rating = item.find("span", class_="rating")["style"]
    rating = int(rating.split(':')[-1].split('%')[0]) // 20

    if rating > 0:
        rating = str(rating) + ' star'
    else:
        rating = "Not Rated"

    return rating

def _extract_commitment(item):
    commitment_span = item.find("span", class_="text-uppercase")

    if commitment_span is not None:
        anchor = commitment_span.find("a")
        return anchor.text.strip()

    return None

def _extract_commitment_url(item):
    commitment_span = item.find("span", class_="text-uppercase")

    if commitment_span is not None:
        anchor = commitment_span.find("a")
        return PREFIX + anchor["href"]

    return None

def _extract_player_id(item):
    name_anchor = item.find("a", class_="bd")

    return name_anchor["href"].split('/')[-1].split('-')[-1]

def _extract_player_name(item):
    name_anchor = item.find("a", class_="bd")

    return name_anchor.text.strip()

def _extract_player_url(item):
    name_anchor = item.find("a", class_="bd")

    return PREFIX + name_anchor["href"]

def _get_searched_player(element):
    return {
        "id": _extract_player_id(element),
        "name": _extract_player_name(element),
        "url": _extract_player_url(element),
        "imageUrl": _extract_image_url(element),
        "position": element.find("div", class_="col-position").text.strip(),
        "club": _extract_club(element),
        "highSchool": _extract_high_school(element),
        "rating": _extract_rating(element),
        "year": element.find("div", class_="col-grad").text.strip(),
        "state": element.find("div", class_="col-state").text.strip(),
        "commitment": _extract_commitment(element),
        "commitmentUrl": _extract_commitment_url(element)
    }

def _get_searched_players(element):
    players = []

    items = element.find_all("div", class_=["item"])
    for item in items:
        players.append(_get_searched_player(item))

    return players

@cache.memoize(timeout=86400)  # cache for 1 day
def search_for_players(gender: str, position: str, grad_year: str, region: str, state: str):
    suffix = _generate_player_suffix(gender, position, grad_year, region, state, 0)

    url = "https://www.topdrawersoccer.com/search/?query="

    response = requests.get(url + suffix)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    players = _get_searched_players(soup)

    pages = _get_search_pages(soup)
    for page in pages:
        suffix = _generate_player_suffix(gender, position, grad_year, region, state, page - 1)

        response = requests.get(url + suffix)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        players.extend(_get_searched_players(soup))

    return players

@cache.memoize(timeout=86400)  # cache for 1 day
def get_commitments_by_club(gender: str, grad_year: int):
    if gender == "female":
        url = f"https://www.topdrawersoccer.com/commitments/club/women/{grad_year}"
    else:
        url = f"https://www.topdrawersoccer.com/commitments/club/men/{grad_year}"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find('table', class_=["table-striped"])

    if table is None:
        return []

    body = table.find('tbody')
    rows = body.find_all("tr")

    records = []
    for row in rows:
        cells = row.findChildren("td")
        record = {
            "club": cells[0].text.strip(),
            "di": int(cells[1].text.strip()),
            "dii": int(cells[2].text.strip()),
            "diii": int(cells[3].text.strip()),
            "naia": int(cells[4].text.strip()),
            "total": int(cells[5].text.strip())
        }
        records.append(record)

    return records
