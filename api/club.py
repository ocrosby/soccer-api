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



clubs_parser = ns.parser()
clubs_parser.add_argument("clubs[]", type=str, location="form", action="append")

ecnl_clubs = []
ga_clubs = []

@ns.route("/league/lookup")
@ns.expect(clubs_parser)
class LeagueLookup(Resource):
    @ns.doc("league_lookup")
    @ns.response(HTTPStatus.OK.value, "Get the organization list", [league_lookup_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(league_lookup_model)
    def post(self):
        """Lookup club leagues"""
        global ecnl_clubs
        global ga_clubs

        result = []

        search = utils.ClubSearch()

        args = clubs_parser.parse_args()
        clubs = args["clubs[]"]

        if ecnl_clubs is None or len(ecnl_clubs) == 0:
            ecnl_clubs = search.get_ecnl_clubs()

        if ga_clubs is None or len(ga_clubs) == 0:
            ga_clubs = search.get_ga_clubs()

        for club_name in clubs:
            league = utils.get_league(club_name, ecnl_clubs, ga_clubs)
            club = { "club": club_name, "league": league }
            result.append(club)

        return result
