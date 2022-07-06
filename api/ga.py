from http import HTTPStatus
from bs4 import BeautifulSoup

import requests
from flask_restx import Namespace, Resource, fields
from requests.exceptions import HTTPError

ns = Namespace("ga", description="Girls Academy related operations")

club_model = ns.model(
    "GA Club",
    {
        "name": fields.String(required=True, description="The club name"),
        "state": fields.String(required=False, description="The club state"),
        "conference": fields.String(required=True, description="The club conference"),
        "url": fields.String(required=True, description="The club url")
    },
)

conference_model = ns.model(
    "GA Conference",
    {
        "name": fields.String(required=True, description="The conference name")
    }
)

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
        club = { "name": anchor.text.strip(), "state": get_state_from_item(item), "conference": get_conference_name_from_cell(cell), "url": anchor["href"] }
        clubs.append(club)

    return clubs

@ns.route("/clubs")
class ClubList(Resource):
    @ns.doc("list_clubs")
    @ns.response(HTTPStatus.OK.value, "Get the Girls Academy club list", [club_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(club_model)
    def get(self):
        """List all clubs"""

        url = "https://girlsacademyleague.com/members/"

        try:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, "html.parser")

            tabs = soup.find_all("div", class_=["et_pb_tab_content"])

            clubs = []
            for tab in tabs:
                cells = tab.find_all("td")

                if len(cells) == 0:
                    continue # Skip over any tabs without cells

                first_cell = cells[0]

                clubs.extend(get_clubs_from_cell(first_cell))

            return clubs

        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )

@ns.route("/conferences")
class ConferenceList(Resource):
    @ns.doc("list_conferences")
    @ns.response(HTTPStatus.OK.value, "Get the Girls Academy conference list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(conference_model)
    def get(self):
        """List all conferences"""

        url = "https://girlsacademyleague.com/members/"

        try:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, "html.parser")

            tabs = soup.find_all("div", class_=["et_pb_tab_content"])

            conferences = []
            for tab in tabs:
                cells = tab.find_all("td")

                if len(cells) == 0:
                    continue # Skip over any tabs without cells

                first_cell = cells[0]

                conference_name = get_conference_name_from_cell(first_cell)
                conference = { "name": conference_name }

                conferences.append(conference)

            return conferences

        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )
