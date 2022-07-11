from http import HTTPStatus

from flask_restx import Namespace, Resource, fields, reqparse
from requests.exceptions import HTTPError

from common import utils

ns = Namespace("club", description="Generic club related operations")

league_lookup_model = ns.model(
    "LeagueLookup",
    {
        "club": fields.String(required=True, description="The name of the club"),
        "league": fields.String(required=True, description="The name of the league")
    }
)

def is_ecnl_club(club_name, ecnl_clubs):
    if club_name is None:
        return False

    if ecnl_clubs is None:
        return False

    club_name = club_name.strip().lower()
    for club in ecnl_clubs:
        if club["name"].strip().lower() == club_name:
            return True

    return False

def is_ga_club(club_name, ga_clubs):
    if club_name is None:
        return False

    if ga_clubs is None:
        return False

    club_name = club_name.strip().lower()
    for club in ga_clubs:
        if club["name"].strip().lower() == club_name:
            return True

    return False

def get_league(club_name, ecnl_clubs, ga_clubs):
    if is_ecnl_club(club_name, ecnl_clubs):
        return "ECNL"

    if is_ga_club(club_name, ga_clubs):
        return "GA"

    return None

clubs_parser = ns.parser()
clubs_parser.add_argument("clubs[]", type=str, location="form", action="append")

@ns.route("/league/lookup")
@ns.expect(clubs_parser)
class CollegeOrganizations(Resource):
    @ns.doc("league_lookup")
    @ns.response(HTTPStatus.OK.value, "Get the organization list", [league_lookup_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(league_lookup_model)
    def post(self):
        """Lookup club leagues"""
        result = []

        search = utils.ClubSearch()

        args = clubs_parser.parse_args()
        clubs = args["clubs[]"]
        ecnl_clubs = search.get_ecnl_clubs()
        ga_clubs = search.get_ga_clubs()

        for club_name in clubs:
            club = { "club": club_name, "league": get_league(club_name, ecnl_clubs, ga_clubs) }
            result.append(club)

        return result
