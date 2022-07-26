from http import HTTPStatus

import flask

from pprint import pprint
from flask_restx import Namespace, Resource, fields, reqparse
from requests.exceptions import HTTPError

from common import utils
from common.extensions import cache

ns = Namespace("sw", description="SoccerWire related operations")

player_model = ns.model(
    "Player",
    {
        "name": fields.String(required=True, description="The name of the player"),
        "position": fields.String(
            required=True, description="The position of the player"
        ),
        "club": fields.String(required=True, description="The club of the player"),
        "league": fields.String(required=False, description="The league of the player"),
        "state": fields.String(required=True, description="The players home state"),
        "commitment": fields.String(
            required=False, description="The players commitment"
        ),
        "commitmentUrl": fields.String(
            required=False, description="The committed schools URL"
        )
    }
)

commitments_parser = reqparse.RequestParser(bundle_errors=True)
commitments_parser.add_argument(
    "team",
    type=str,
    location="json",
    default=None,
    help='Bad choice: {error_msg}'
)
commitments_parser.add_argument(
    "club",
    type=str,
    location="json",
    default=None,
    help='Bad choice: {error_msg}'
)
commitments_parser.add_argument(
    "positions",
    type=str,
    location="json",
    default=None,
    help='Bad choice: {error_msg}'
)
commitments_parser.add_argument(
    "state",
    type=str,
    location="json",
    default=None,
    help='Bad choice: {error_msg}'
)


@ns.route("/commitments")
@ns.expect(commitments_parser)
class Commitments(Resource):
    @ns.doc("player_search")
    @ns.response(HTTPStatus.OK.value, "Search for players", [player_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(player_model)
    def post(self):
        """Search for college commitments"""
        try:
            args = commitments_parser.parse_args()

            print(args)

            player_search = utils.PlayerSearch()
            players = player_search.get_players(args)

            return players
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            pprint(err.data["errors"])
            print(f"Other error occurred: {err}")
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )
