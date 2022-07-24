import requests

from bs4 import BeautifulSoup

from common.extensions import cache

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
def get_conference_commits(gender: str, division: str, conference_name: str):
    schools = []
    players = []

    content = get_conference_commitments_content(gender, division, conference_name)

    soup = BeautifulSoup(content, "html.parser")
    

    return (schools, players)
