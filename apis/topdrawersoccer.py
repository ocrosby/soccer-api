from email.policy import default
import requests

from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from http import HTTPStatus
from flask import jsonify
from flask_restx import Namespace, Resource, fields

ns = Namespace('tds', description='TopDrawerSoccer related operations')

conference_model = ns.model('Conference', {
    'id': fields.Integer(required=True, description='The identifier of the conference.'),
    'name': fields.String(required=True, description='The conference name'),
    'url': fields.String(required=True, description='The conference url')
})

# /college/conferences/<gender:string>
# /college/teams/<gender:string>
# /college/commitments/<gender:string>,<year:int>
# /college/commitments/conference/<gender:string>,<year:int>

# /college/conference/details/<name:string>

division_mapping = {
    "di": "/di/divisionid-1",
    "dii": "/dii/divisionid-2",
    "diii": "/diii/divisionid-3",
    "naia": "/naia/divisionid-4",
    "njcaa": "/njcaa/divisionid-5"
}

player_model = ns.model('Player', {
    'id': fields.Integer(required=True, description='The identifier of the player.'),
    'name': fields.String(required=True, description='The name of the player'),
    'url': fields.String(required=True, description='The URL of the player'),
    'image_url': fields.String(required=True, description='The URL of the players image'),
    'position': fields.String(required=True, description='The position of the player'),
    'club': fields.String(required=True, description='The club of the player'),
    'high_school': fields.String(required=True, description='The players high school'),
    'rating': fields.String(required=False, description='The rating of the player'),
    'year': fields.Integer(required=True, description='The graduation year of the player'),
    'state': fields.String(required=True, description='The players home state'),
    'commitment': fields.String(required=False, description='The players commitment'),
    'commitment_url': fields.String(required=False, description='The committed schools URL')
})

players_parser = ns.parser()
players_parser.add_argument("name", type=str, location="form")
players_parser.add_argument("position", type=str, location="form", choices=("All", "Goalkeeper", "Defender", "Midfielder", "Forward"), default="All")
players_parser.add_argument("grad_year", type=str, location="form", choices=("2023", "2024", "2025", "2026"), default="2023")
players_parser.add_argument("region", type=str, location="form", choices=("All", "Florida", "Great Lakes", "Heartland", "International", "Mid Atlantic", "Midwest", "New Jersey", "New York", "Northeast", "Northern California & Hawaii", "Pacific Northwest", "Pennsylvania", "Rocky Mountains & Southwest", "South", "South Atlantic", "Southern California", "Texas"), default="All")
players_parser.add_argument("state", type=str, location="form", choices=("All", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "International", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"), default="All")
players_parser.add_argument("gender", type=str, location="form", choices=("All", "Male", "Female"), default="All")

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

def get_gender_id(args):
    gender = args["gender"]

    if gender is None:
        return ""

    gender = gender.lower()
    if gender in ["female", "f"]:
        return "f"

    if gender in ["male", "m"]:
        return "m"

    return ""

def get_position_id(args):
    position = args["position"]

    if position is None:
        return "0"

    if position in position_lookup:
        return position_lookup[position]

    return "0"

def get_grad_year(args):
    grad_year = args["grad_year"]

    if grad_year is None:
        return ""

    return grad_year

def get_region_id(args):
    region = args["region"]

    if region is None:
        return "0"

    if region in region_lookup:
        return region_lookup[region]

    return "0"

def get_state_id(args):
    state = args["state"]

    if state is None:
        return "0"

    if state in state_lookup:
        return state_lookup[state]

    return 0

def generate_player_suffix(args, page_number):
    suffix = "&genderId=" + get_gender_id(args)
    suffix += "&positionId=" + str(get_position_id(args))
    suffix += "&graduationYear=" + get_grad_year(args)
    suffix += "&regionId=" + str(get_region_id(args))
    suffix += "&countyId=" + str(get_state_id(args))
    suffix += "&pageNo=" + str(page_number)
    suffix += "&area=clubplayer&sortColumns=0&sortDirections=1&search=1"

    return suffix

@ns.route('/players')
@ns.expect(players_parser)
class PlayerSearch(Resource):
    @ns.doc('player_search')
    @ns.response(HTTPStatus.OK.value, "Search for players", [player_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(player_model)
    def post(self):
        '''Search for players'''

        players = []

        url = "https://www.topdrawersoccer.com/search/?query="

        try:
            args = players_parser.parse_args()

            suffix = generate_player_suffix(args, 0)
            response = requests.get(url + suffix)

            soup = BeautifulSoup(response.content, "html.parser")

            items = soup.find_all("div", class_=["item"])

            for item in items:
                player = {}

                name_anchor = item.find("a", class_="bd")

                player["id"] = name_anchor["href"].split('/')[-1].split('-')[-1]
                player["name"] = name_anchor.text.strip()

                print(player["name"])

                buffer = item.find("div", class_="ml-2").text.strip()
                target = buffer.split('\t\t\t\t')[1].strip()
                pieces = target.split('/')

                if len(pieces) == 1:
                    club = pieces[0]
                    high_school = None
                elif len(pieces) == 2:
                    club = pieces[0]
                    high_school = pieces[1]
                else:
                    club = None
                    high_school = None

                player["url"] = name_anchor["href"]

                image = item.find("img", class_="imageProfile")

                if image is not None:
                    player["image_url"] = image["src"]
                else:
                    player["image_url"] = None

                player["position"] = item.find("div", class_="col-position").text.strip()
                player["club"] = club
                player["high_school"] = high_school

                rating = item.find("span", class_="rating")["style"]
                rating = int(rating.split(':')[-1].split('%')[0]) // 20
                rating = str(rating) + ' star'

                player["rating"] = rating
                player["year"] = item.find("div", class_="col-grad").text.strip()
                player["state"] = item.find("div", class_="col-state").text.strip()
                player["commitment"] = None # Assume they aren't committed
                player["commitment_url"] = None

                # Figure out if they are committed.
                commitment_span = item.find("span", class_="text-uppercase")
                if commitment_span is not None:
                    # committed
                    anchor = commitment_span.find("a")
                    player["commitment"] = anchor.text.strip()
                    player["commitment_url"] = anchor["href"]

                players.append(player)


            # /search/?query=&genderId=&positionId=5&graduationYear=&regionId=0&countyId=0&pageNo=0&area=clubplayer&sortColumns=0&sortDirections=1&search=1

            # response = requests.post(url)

            return players
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")

@ns.route('/college/conferences/<string:gender>/<string:division>')
@ns.param('gender', 'The target gender [male|female]')
@ns.param('division', 'The target division [di|dii|diii|naia|njcaa] (defaults to di)')
class ClubList(Resource):
    @ns.doc('list_conferences')
    @ns.response(HTTPStatus.OK.value, "Get the item list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(conference_model)
    def get(self, gender: str, division: str):
        '''List all conferences'''

        url = "https://www.topdrawersoccer.com/college-soccer/college-conferences"

        try:
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
                    id = int(url.split('/')[-1].split('-')[-1])

                    if gender == "male" and "Men's" in heading:
                        conferences.append({ "id": id, "name": name, "url": url})

                    if gender == "female" and "Women's" in heading:
                        conferences.append({ "id": id, "name": name, "url": url})

            return conferences
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")
