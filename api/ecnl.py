from http import HTTPStatus

import requests
from flask_restx import Namespace, Resource, fields
from requests.exceptions import HTTPError
from common import utils

ns = Namespace("ecnl", description="ECNL related operations")

club_model = ns.model(
    "Club",
    {
        "id": fields.Integer(required=True, description="The club identifier"),
        "orgId": fields.Integer(
            required=True, description="The organization identifier"
        ),
        "name": fields.String(required=True, description="The club name"),
        "city": fields.String(required=True, description="The club city"),
        "state": fields.String(required=True, description="the club state"),
        "logo": fields.String(required=True, description="The URL for the club logo"),
    },
)

search = utils.ClubSearch()

@ns.route("/clubs")
class ClubList(Resource):
    @ns.doc("list_clubs")
    @ns.response(HTTPStatus.OK.value, "Get the item list", [club_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(club_model)
    def get(self):
        """List all clubs"""
        global search

        try:
            return search.get_ecnl_clubs()
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )
