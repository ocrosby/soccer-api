from http import HTTPStatus
from bs4 import BeautifulSoup

import requests
from flask_restx import Namespace, Resource, fields
from requests.exceptions import HTTPError
from common import utils

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

search = utils.ClubSearch()

@ns.route("/clubs")
class ClubList(Resource):
    @ns.doc("list_clubs")
    @ns.response(HTTPStatus.OK.value, "Get the Girls Academy club list", [club_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(club_model)
    def get(self):
        """List all clubs"""
        global search

        try:
            return search.get_ga_clubs()
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
