import pprint
import requests

from bs4 import BeautifulSoup

from common.config import CLUB_TRANSLATIONS, GA_CLUBS
from common.extensions import cache

division_mapping = {
    "di": "/di/divisionid-1",
    "dii": "/dii/divisionid-2",
    "diii": "/diii/divisionid-3",
    "naia": "/naia/divisionid-4",
    "njcaa": "/njcaa/divisionid-5"
}

position_lookup = {
    "All": 0,
    "Goalkeeper": 1,
    "Defender": 2,
    "Midfielder": 6,
    "Forward": 5
}

region_lookup = {
    "All": 0,
    "Florida": 10,
    "Great Lakes": 7,
    "Heartland": 5,
    "International": 17,
    "Mid Atlantic": 100,  # or possibly 12
    "Midwest": 6,
    "New Jersey": 14,
    "New York": 15,
    "Northeast": 16,
    "Northern California & Hawaii": 2,
    "Pacific Northwest": 3,
    "Pennsylvania": 13,
    "Rocky Mountains & Southwest": 4,
    "South": 9,
    "South Atlantic": 11,
    "Southern California": 1,
    "Texas": 8
}

state_lookup = {
    "All": 0,
    "Alabama": 1,
    "Alaska": 2,
    "Arizona": 3,
    "Arkansas": 4,
    "California": 5,
    "Colorado": 6,
    "Connecticut": 7,
    "Delaware": 8,
    "District of Columbia": 9,
    "Florida": 10,
    "Georgia": 11,
    "Hawaii": 12,
    "Idaho": 13,
    "Illinois": 14,
    "Indiana": 15,
    "International": 99,
    "Iowa": 16,
    "Kansas": 17,
    "Kentucky": 18,
    "Louisiana": 19,
    "Maine": 20,
    "Maryland": 21,
    "Massachusetts": 22,
    "Michigan": 23,
    "Minnesota": 24,
    "Mississippi": 25,
    "Missouri": 26,
    "Montana": 27,
    "Nebraska": 28,
    "Nevada": 29,
    "New Hampshire": 30,
    "New Jersey": 31,
    "New Mexico": 32,
    "New York": 33,
    "North Carolina": 34,
    "North Dakota": 35,
    "Ohio": 36,
    "Oklahoma": 37,
    "Oregon": 38,
    "Pennsylvania": 39,
    "Rhode Island": 40,
    "South Carolina": 41,
    "South Dakota": 42,
    "Tennessee": 43,
    "Texas": 44,
    "Utah": 45,
    "Vermont": 46,
    "Virginia": 47,
    "Washington": 48,
    "West Virginia": 49,
    "Wisconsin": 50,
    "Wyoming": 51
}


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
        return GA_CLUBS

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


class TransferTracker:
    def __init__(self):
        self.prefix = "https://www.topdrawersoccer.com"

    def extract_position_and_name(self, cell):
        try:
            buffer = cell.text.strip()

            if buffer == "Player":
                return (None, None)

            if "\xa0" in buffer:
                tokens = buffer.split("\xa0")

                position = tokens[0].strip()
                name = tokens[1].strip()
            else:
                tokens = buffer.split(" ")

                position = tokens[0].strip()
                name = " ".join(tokens[1:]).strip()

            print(f"Processing '{name}' ...")

            return (position, name)
        except Exception as err:
            print(err)

    def extract_school_name(self, cell):
        return cell.text.strip()

    def extract_url(self, cell):
        anchor = cell.find("a")

        if anchor is None:
            return None

        url = self.prefix + anchor["href"].strip()

        return url

    def extract_school(self, cell):
        name = self.extract_school_name(cell)
        url = self.extract_url(cell)

        return (name, url)

    def extract_transfer(self, row):
        player = {}

        try:
            cells = row.find_all("td")

            position, name = self.extract_position_and_name(cells[0])
            url = self.extract_url(cells[0])

            if name is None:
                return None

            if len(cells) > 1:
                former_school_name, former_school_url = self.extract_school(cells[1])

                if len(cells) > 2:
                    new_school_name, new_school_url = self.extract_school(cells[2])
                else:
                    new_school_name = None
                    new_school_url = None
            else:
                new_school_name = None
                new_school_url = None
                former_school_name = None
                former_school_url = None

            player["name"] = name
            player["url"] = url
            player["position"] = position
            player["formerSchoolName"] = former_school_name
            player["formerSchoolUrl"] = former_school_url
            player["newSchoolName"] = new_school_name
            player["newSchoolUrl"] = new_school_url
        except Exception as err:
            print(err)
            raise err

        return player

    def get_transfers(self):
        url = "https://www.topdrawersoccer.com/college-soccer-articles/2022-womens-di-transfer-tracker_aid50187"

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find_all("tr")

        transfers = []
        for row in rows:
            player = self.extract_transfer(row)

            if player is None:
                continue

            if len(player["name"]) == 0:
                continue

            transfers.append(player)

        return transfers

class PlayerSearch:
    def __init__(self):
        """Constructor"""
        self.soup = None
        self.prefix = "https://www.topdrawersoccer.com"

    def get_gender_id(self, args):
        gender = args["gender"]

        if gender is None:
            return ""

        gender = gender.lower()
        if gender in ["female", "f"]:
            return "f"

        if gender in ["male", "m"]:
            return "m"

        return ""

    def get_position_id(self, args):
        position = args["position"]

        if position is None:
            return "0"

        if position in position_lookup:
            return position_lookup[position]

        return "0"

    def get_grad_year(self, args):
        grad_year = args["gradyear"]

        if grad_year is None:
            return ""

        return grad_year

    def get_region_id(self, args):
        region = args["region"]

        if region is None:
            return "0"

        if region in region_lookup:
            return region_lookup[region]

        return "0"

    def get_state_id(self, args):
        state = args["state"]

        if state is None:
            return "0"

        if state in state_lookup:
            return state_lookup[state]

        return 0

    def generate_player_suffix(self, args, page_offset):
        suffix = "&genderId=" + self.get_gender_id(args)
        suffix += "&positionId=" + str(self.get_position_id(args))
        suffix += "&graduationYear=" + self.get_grad_year(args)
        suffix += "&regionId=" + str(self.get_region_id(args))
        suffix += "&countyId=" + str(self.get_state_id(args))
        suffix += "&pageNo=" + str(page_offset)
        suffix += "&area=clubplayer&sortColumns=0&sortDirections=1&search=1"

        return suffix

    def extract_pages_list(self):
        pagination = self.soup.find("ul", class_=["pagination"])
        page_items = pagination.findChildren("li", class_=["page-item"])

        pages = []
        for page_item in page_items:
            text = page_item.text.strip()

            if text in ["Previous", "1", "Next"]:
                continue

            pages.append(int(text))

        return pages

    def load_page(self, args, page_offset):
        suffix = self.generate_player_suffix(args, page_offset)

        url = "https://www.topdrawersoccer.com/search/?query="

        response = requests.get(url + suffix)

        self.soup = BeautifulSoup(response.content, "html.parser")

    def extract_club(self, item):
        buffer = item.find("div", class_="ml-2").text.strip()
        target = buffer.split('\t\t\t\t')[1].strip()
        pieces = target.split('/')

        if len(pieces) >= 1:
            return pieces[0]

        return None

    def extract_high_school(self, item):
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

    def extract_image_url(self, item):
        image = item.find("img", class_="imageProfile")

        if image is not None:
            return self.prefix + image["src"]

        return None

    def extract_rating(self, item):
        rating = item.find("span", class_="rating")["style"]
        rating = int(rating.split(':')[-1].split('%')[0]) // 20

        if rating > 0:
            rating = str(rating) + ' star'
        else:
            rating = "Not Rated"

        return rating

    def extract_commitment(self, item):
        commitment_span = item.find("span", class_="text-uppercase")

        if commitment_span is not None:
            anchor = commitment_span.find("a")
            return anchor.text.strip()

        return None

    def extract_commitment_url(self, item):
        commitment_span = item.find("span", class_="text-uppercase")

        if commitment_span is not None:
            anchor = commitment_span.find("a")
            return self.prefix + anchor["href"]

        return None

    def extract_player_id(self, item):
        name_anchor = item.find("a", class_="bd")

        return name_anchor["href"].split('/')[-1].split('-')[-1]

    def extract_player_name(self, item):
        name_anchor = item.find("a", class_="bd")

        return name_anchor.text.strip()

    def extract_player_url(self, item):
        name_anchor = item.find("a", class_="bd")

        return self.prefix + name_anchor["href"]

    def extract_player(self, item):
        player = {}

        player["id"] = self.extract_player_id(item)
        player["name"] = self.extract_player_name(item)
        player["url"] = self.extract_player_url(item)
        player["image_url"] = self.extract_image_url(item)
        player["position"] = item.find("div", class_="col-position").text.strip()
        player["club"] = self.extract_club(item)
        player["high_school"] = self.extract_high_school(item)
        player["rating"] = self.extract_rating(item)
        player["year"] = item.find("div", class_="col-grad").text.strip()
        player["state"] = item.find("div", class_="col-state").text.strip()
        player["commitment"] = self.extract_commitment(item)
        player["commitment_url"] = self.extract_commitment_url(item)

        return player

    def extract_players(self):
        players = []

        items = self.soup.find_all("div", class_=["item"])

        for item in items:
            player = self.extract_player(item)
            players.append(player)

        return players

    @cache.memoize(timeout=604800)
    def get_players(self, args):
        self.load_page(args, 0)

        players = self.extract_players()

        pages = self.extract_pages_list()
        for page in pages:
            self.load_page(args, page-1)
            players.extend(self.extract_players())

        return players


@cache.memoize(timeout=604800)
def is_ecnl_club(target_club_name, ecnl_clubs):
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


# @cache.memoize(timeout=604800)
def is_ga_club(target_club_name, ga_clubs):
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


@cache.memoize(timeout=604800)
def get_league(club_name, ecnl_clubs, ga_clubs):
    if is_ecnl_club(club_name, ecnl_clubs):
        return "ECNL"

    if is_ga_club(club_name, ga_clubs):
        return "GA"

    print("Could not find the club (" + club_name + ")")

    return None

# Could not find the club (FC Fury NY)
# Could not find the club (Georgia Rush)
# Could not find the club (Libertyville FC)
# Could not find the club (San Jose Earthquakes)
# Could not find the club (Washington Spirit Academy MD)
# Could not find the club (CCV Stars)
# Could not find the club (Excel Soccer Academy)
# Could not find the club (Arizona Arsenal)
# Could not find the club (California Thorns FC)
# Could not find the club (Cincinnati Development Academy)
# Could not find the club (New Jersey Stallions Academy)
# Could not find the club (Sporting Columbus)
# Could not find the club (Team Chicago)
# Could not find the club (Tudela Football Club)
# Could not find the club (Cleveland Soccer Academy)
# Could not find the club (Las Vegas Premier)
# Could not find the club (Sockers FC)
# Could not find the club (Sporting Arsenal FC (CA))
# Could not find the club (Blues Youth SC (fka Corona United))
# Could not find the club (Bozeman Blitzz)
# Could not find the club (California Thorns FC)
# Could not find the club (West Coast Football Club)
# Could not find the club (California Thorns FC)
# Could not find the club (LA Galaxy)
# Could not find the club (Los Angeles Premier FC)
# Could not find the club (Mtn. View Los Altos SC)
# Could not find the club (Northwest Elite)
# Could not find the club (Placer United SC)
# Could not find the club (NYCFC)
# Could not find the club (Real Salt Lake (AZ))
# Could not find the club (Soccer Vision Academy)
# Could not find the club (Bavarian SC)
# Could not find the club (Cincinnati Development Academy)
# Could not find the club (Jackson FC)
# Could not find the club (Shattuck St. Mary's Academy)
# Could not find the club (Sockers FC)
# Could not find the club (San Jose Earthquakes)
# Could not find the club (Fever United Football Club)

search = ClubSearch()


class TopDrawerSoccer:
    def __init__(self):
        """Constructor"""
        self.prefix = "https://www.topdrawersoccer.com"

    def apply_club_translations(self, schools):
        for school in schools:
            for player in school['players']:
                club = player['club']
                if club in CLUB_TRANSLATIONS:
                    player['club'] = CLUB_TRANSLATIONS[club]

    def expand_player_details(self, player):
        # Initialize the new properties.
        if "club" not in player:
            player["club"] = None

        player["team"] = None
        player["jerseyNumber"] = None
        player["highSchool"] = None
        player["region"] = None

        if player is None:
            return

        if "url" not in player:
            return

        # print("Making an additional request for " + player["name"] + ".")
        response = requests.get(player["url"])

        soup = BeautifulSoup(response.content, "html.parser")


        search = PlayerSearch()
        player["rating"] = search.extract_rating(soup)

        position_element = soup.find("div", class_=["player-position"])
        buffer = position_element.text.strip()
        items = buffer.split("-")
        position = items[0].strip()

        commitment_anchor = position_element.find('a')
        if commitment_anchor is not None:
            player["commitment"] = commitment_anchor.text.strip()
            player["commitmentUrl"] = self.prefix + commitment_anchor["href"]

        if len(position) > 0:
            player["position"] = position

        container = soup.find("ul", class_=["profile_grid"])
        items = container.findChildren('li')

        for item in items:
            (lvalue, rvalue) = item.text.strip().split(':')

            lvalue = lvalue.strip()
            rvalue = rvalue.strip()

            if lvalue == "Club":
                player["club"] = rvalue
            elif lvalue == "Team Name":
                player["team"] = rvalue
            elif lvalue == "Jersey Number":
                player["jerseyNumber"] = rvalue
            elif lvalue == "High School":
                player["highSchool"] = rvalue
            elif lvalue == "Region":
                player["region"] = rvalue
            else:
                print("Unknown lvalue " + lvalue + " on player detail page " + player["url"] + ".")


    @cache.memoize(timeout=604800)
    def get_conference_commits(self, gender: str, division: str, name: str, year: int):
        global search

        print(f"Commits for gender={gender}, division={division}, conference={name}, year={year}")

        try:
            conference = self.get_conference(gender, division, name)

            url = conference['url'] + "/tab-commitments#commitments"

            page = requests.get(url)

            soup = BeautifulSoup(page.content, "html.parser")

            tables = soup.find_all(
                "table", class_=["table-striped", "tds-table", "female"])

            body = None
            for table in tables:
                header = table.find("thead", class_="female")
                if header is not None:
                    body = table.find("tbody")

            schools = []
            if body is not None:
                rows = body.find_all("tr")

                for row in rows:
                    columns = row.find_all("td")
                    if len(columns) == 1:
                        name = columns[0].text.strip()
                        school = {"name": name, "players": []}
                        schools.append(school)
                    else:
                        player = {"name": None, "year": None, "position": None,
                                  "city": None, "state": None, "club": None}
                        player["name"] = columns[0].text.strip()
                        player["url"] = self.prefix + columns[0].find('a')['href']
                        player["year"] = columns[1].text.strip()
                        player["position"] = columns[2].text.strip()
                        player["city"] = columns[3].text.strip()
                        player["state"] = columns[4].text.strip()
                        player["club"] = columns[5].text.strip()

                        self.expand_player_details(player)

                        # Replace multiple spaces in the club name
                        while "  " in player["club"]:
                            player["club"].replace("  ", " ")

                        if int(player["year"]) == year:
                            school["players"].append(player)

                self.apply_club_translations(schools)

                # Collect a unique list of clubs
                clubs = []
                for school in schools:
                    for player in school["players"]:
                        current_club = player["club"]

                        if current_club is None:
                            continue

                        current_club = current_club.strip()
                        if len(current_club) == 0:
                            continue

                        if current_club in clubs:
                            continue

                        clubs.append(current_club)

                # Sort the list of clubs
                clubs.sort()

                ecnl_clubs = search.get_ecnl_clubs()
                ga_clubs = search.get_ga_clubs()

                mapping = {}
                for club_name in clubs:
                    mapping[club_name] = get_league(club_name, ecnl_clubs, ga_clubs)

                # pprint.pprint(mapping)

                for school in schools:
                    for player in school["players"]:
                        club = player["club"]

                        if club is None or len(club) == 0:
                            player["league"] = "Other"
                        else:
                            if club in mapping:
                                player["league"] = mapping[club]

                        if player["league"] is None:
                            player["league"] = "Other"

        except Exception as err:
            print(err)

        return schools

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
        if division in division_mapping:
            suffix = division_mapping[division]

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

                # schools = self.get_conference_commits(gender, division, name)
                schools = None

                if gender == "male" and "Men's" in heading:
                    conferences.append(
                        {"id": conference_id, "name": name, "url": url, "schools": schools})

                if gender == "female" and "Women's" in heading:
                    conferences.append(
                        {"id": conference_id, "name": name, "url": url, "schools": schools})

        return conferences
