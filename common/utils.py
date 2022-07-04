import requests

from bs4 import BeautifulSoup

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
    "Mid Atlantic": 100, # or possibly 12
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
        grad_year = args["grad_year"]

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

    def get_players(self, args):
        self.load_page(args, 0)

        players = self.extract_players()

        pages = self.extract_pages_list()
        for page in pages:
            self.load_page(args, page-1)
            players.extend(self.extract_players())

        return players
class TopDrawerSoccer:
    def __init__(self):
        """Constructor"""
        pass

    def get_conference_commits(self, gender: str, division: str, name: str, year: int):
        conference = self.get_conference(gender, division, name)

        url = conference['url'] + "/tab-commitments#commitments"

        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")

        tables = soup.find_all("table", class_=["table-striped", "tds-table", "female"])

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
                    school = { "name": name, "players": [] }
                    schools.append(school)
                else:
                    player = { "name": None, "year": None, "position": None, "city": None, "state": None, "club": None }
                    player["name"] = columns[0].text.strip()
                    player["year"] = columns[1].text.strip()
                    player["position"] = columns[2].text.strip()
                    player["city"] = columns[3].text.strip()
                    player["state"] = columns[4].text.strip()
                    player["club"] = columns[5].text.strip()

                    if int(player["year"]) == year:
                        school["players"].append(player)

        return schools


    def get_conference(self, gender: str, division: str, name: str):
        conferences = self.get_conferences(gender, division)

        for conference in conferences:
            if conference['name'] == name:
                return conference

        return None

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
                    conferences.append({ "id": conference_id, "name": name, "url": url, "schools": schools})

                if gender == "female" and "Women's" in heading:
                    conferences.append({ "id": conference_id, "name": name, "url": url, "schools": schools})

        return conferences
