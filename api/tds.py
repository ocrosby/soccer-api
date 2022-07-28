from dbm.ndbm import library
from http import HTTPStatus

import flask

from pprint import pprint
from flask_restx import Namespace, Resource, fields, reqparse
from requests.exceptions import HTTPError

from common import utils
from common.extensions import cache

from common import config

from lib import topdrawer

ns = Namespace("tds", description="TopDrawerSoccer related operations")

college_organization_model = ns.model(
    "Organization",
    {
        "id": fields.String(required=True, description="The organization identifier"),
        "name": fields.String(required=True, description="The organization name"),
    },
)

college_division_model = ns.model(
    "Division",
    {
        "divisionId": fields.String(
            required=True, description="The division identifier"
        ),
        "divisionName": fields.String(required=True, description="The division name"),
        "orgId": fields.String(
            required=True, description="The organization identifier"
        ),
    },
)

player_model = ns.model(
    "Player",
    {
        "name": fields.String(required=True, description="The player name"),
        "url": fields.String(required=True, description="The players TopDrawerSoccer URL"),
        "year": fields.String(required=True, description="The players graduation year"),
        "position": fields.String(required=True, description="The players position"),
        "city": fields.String(required=True, description="The players home city"),
        "state": fields.String(required=True, description="The players home state"),
        "club": fields.String(required=True, description="The players club"),
        "team": fields.String(required=True, description="The players team"),
        "jerseyNumber": fields.String(required=True, description="The players jersey number"),
        "highSchool": fields.String(required=True, description="The players high school"),
        "region": fields.String(required=True, description="The players region"),
        "rating": fields.String(required=True, description="The players rating"),
        "league": fields.String(required=False, description="The players league"),
        "commitment": fields.String(required=False, description="The players commitment"),
        "commitmentUrl": fields.String(required=False, description="The players commitment URL")
    },
)

school_model = ns.model(
    "School",
    {
        "clgid": fields.Integer(required=False, description="The TopDrawerSoccer identifier for the school", default=-1),
        "url": fields.String(required=False, description="The TopDrawerSoccer URL for the school", default=None),
        "name": fields.String(required=True, description="The school name"),
        "players": fields.List(fields.Nested(player_model)),
    },
)

commitments_by_club_model = ns.model(
    "CommitmentsByClub",
    {
        "club": fields.String(required=True, description="The club name"),
        "di": fields.Integer(required=True, description="The number of DI commits."),
        "dii": fields.Integer(required=True, description="The number of DII commits."),
        "diii": fields.Integer(required=True, description="The number of DII commits."),
        "naia": fields.Integer(required=True, description="The number of NAIA commits."),
        "total": fields.Integer(required=True, description="The total number of commits.")
    }
)

conference_model = ns.model(
    "Conference",
    {
        "id": fields.Integer(
            required=True, description="The identifier of the conference."
        ),
        "name": fields.String(required=True, description="The conference name"),
        "url": fields.String(required=True, description="The conference url"),
        "schools": fields.List(fields.Nested(school_model)),
    },
)

# /college/conferences/<gender:string>
# /college/teams/<gender:string>
# /college/commitments/<gender:string>,<year:int>
# /college/commitments/conference/<gender:string>,<year:int>

# /college/conference/details/<name:string>

tds = utils.TopDrawerSoccer()

gender_parser = reqparse.RequestParser()
gender_parser.add_argument("gender", type=str, choices=("male", "female"))

division_parser = reqparse.RequestParser()
division_parser.add_argument(
    "division", type=str, choices=("di", "dii", "diii", "naia", "njcaa")
)


@ns.route("/college/organizations")
class CollegeOrganizations(Resource):
    @ns.doc("list_college_organizations")
    @ns.response(HTTPStatus.OK.value, "Get the organization list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(college_organization_model)
    def get(self):
        """List all college organizations"""
        return config.COLLEGE_ORGANIZATIONS


@ns.route("/college/divisions")
class CollegeDivisions(Resource):
    @ns.doc("list_college_divisions")
    @ns.response(HTTPStatus.OK.value, "Get the division list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(college_division_model)
    def get(self):
        """List all college divisions"""
        return config.COLLEGE_DIVISIONS


player_model = ns.model(
    "Player",
    {
        "id": fields.Integer(
            required=True, description="The identifier of the player."
        ),
        "name": fields.String(required=True, description="The name of the player"),
        "url": fields.String(required=True, description="The URL of the player"),
        "imageUrl": fields.String(
            required=True, description="The URL of the players image"
        ),
        "position": fields.String(
            required=True, description="The position of the player"
        ),
        "club": fields.String(required=True, description="The club of the player"),
        "league": fields.String(required=False, description="The league of the player"),
        "highSchool": fields.String(
            required=True, description="The players high school"
        ),
        "rating": fields.String(required=False, description="The rating of the player"),
        "year": fields.Integer(
            required=True, description="The graduation year of the player"
        ),
        "state": fields.String(required=True, description="The players home state"),
        "commitment": fields.String(
            required=False, description="The players commitment"
        ),
        "commitmentUrl": fields.String(
            required=False, description="The committed schools URL"
        )
    }
)

transfer_model = ns.model(
    "Transfer",
    {
        "name": fields.String(required=True, description="The players name"),
        "url": fields.String(required=False, description="The players URL"),
        "position": fields.String(required=True, description="The players position"),
        "formerSchoolName": fields.String(required=True, description="The players former school name"),
        "formerSchoolUrl": fields.String(required=False, description="The URL of the players former school"),
        "newSchoolName": fields.String(required=True, description="The players new school name"),
        "newSchoolUrl": fields.String(required=False, description="the URL of the players new school")
    }
)


players_parser = reqparse.RequestParser(bundle_errors=True)
players_parser.add_argument("name", type=str, location="json")
players_parser.add_argument(
    "position",
    type=str,
    location="json",
    choices=("All", "Goalkeeper", "Defender", "Midfielder", "Forward"),
    default="All",
    help='Bad choice: {error_msg}'
)
players_parser.add_argument(
    "gradyear",
    type=str,
    location="json",
    choices=("2022", "2023", "2024", "2025", "2026"),
    default="2023",
    help='Bad choice: {error_msg}'
)
players_parser.add_argument(
    "region",
    type=str,
    location="json",
    choices=(
        "All",
        "Florida",
        "Great Lakes",
        "Heartland",
        "International",
        "Mid Atlantic",
        "Midwest",
        "New Jersey",
        "New York",
        "Northeast",
        "Northern California & Hawaii",
        "Pacific Northwest",
        "Pennsylvania",
        "Rocky Mountains & Southwest",
        "South",
        "South Atlantic",
        "Southern California",
        "Texas",
    ),
    default="All",
    help='Bad choice: {error_msg}'
)
players_parser.add_argument(
    "state",
    type=str,
    location="json",
    choices=(
        "All",
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "Delaware",
        "District of Columbia",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "International",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
    ),
    default="All",
    help='Bad choice: {error_msg}'
)
players_parser.add_argument(
    "gender",
    type=str,
    location="json",
    choices=("All", "Male", "Female"),
    default="All",
    help='Bad choice: {error_msg}'
)


@ns.route("/college/transfers")
class TransferTracker(Resource):
    @ns.doc("transfer_tracker")
    @ns.response(HTTPStatus.OK.value, "Search for transfers", [transfer_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(transfer_model)
    def get(self):
        """Get the transfers"""
        try:
            return topdrawer.get_transfers()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            print(f"Other error occurred: {err}")
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )


def _get_gender_id(args):
    gender = args["gender"]

    if gender is None:
        return ""

    gender = gender.lower()
    if gender in ["female", "f"]:
        return "f"

    if gender in ["male", "m"]:
        return "m"

    return ""


def _get_position_id(args):
    position = args["position"]

    if position is None:
        return "0"

    if position in config.POSITION_LOOKUP:
        return config.POSITION_LOOKUP[position]

    return "0"


def _get_grad_year(args):
    grad_year = args["gradyear"]

    if grad_year is None:
        return ""

    return grad_year


def _get_region_id(args):
    region = args["region"]

    if region is None:
        return "0"

    if region in config.REGION_LOOKUP:
        return config.REGION_LOOKUP[region]

    return "0"


def _get_state_id(args):
    state = args["state"]

    if state is None:
        return "0"

    if state in config.STATE_LOOKUP:
        return config.STATE_LOOKUP[state]

    return 0


@ns.route("/players")
@ns.expect(players_parser)
class PlayerSearch(Resource):
    @ns.doc("player_search")
    @ns.response(HTTPStatus.OK.value, "Search for players", [player_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(player_model)
    def post(self):
        """Search for players"""
        try:
            args = players_parser.parse_args()

            gender = _get_gender_id(args)
            position = _get_position_id(args)
            grad_year = _get_grad_year(args)
            region = _get_region_id(args)
            state = _get_state_id(args)

            return topdrawer.search_for_players(gender, position, grad_year, region, state)
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


conferences_parser = ns.parser()
conferences_parser.add_argument(
    "gender",
    type=str,
    location="args",
    choices=("all", "male", "female"),
    default="female",
)
conferences_parser.add_argument(
    "division",
    type=str,
    location="args",
    choices=("di", "dii", "diii", "naia", "njcaa"),
    default="di",
)


@ns.route("/college/conferences/<string:gender>/<string:division>")
@ns.expect(conferences_parser)
class ConferenceList(Resource):
    @ns.doc("list_conferences")
    @ns.response(HTTPStatus.OK.value, "Get the item list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(conference_model)
    def get(self, gender: str, division: str):
        """List all conferences"""
        try:
            return tds.get_conferences(gender, division)
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )


@ns.route("/college/conference/<string:gender>/<string:division>/<string:name>")
@ns.param("gender", "The gender of the target conference")
@ns.param("division", "The division of the target conference")
@ns.param("name", "The name of the target conference")
class Conference(Resource):
    @ns.doc("get_conference")
    @ns.response(HTTPStatus.OK.value, "Get the conference", conference_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Conference not found")
    @ns.marshal_with(conference_model)
    @cache.memoize(timeout=604800)
    def get(self, gender: str, division: str, name: str):
        """Get a conference by name"""
        try:
            conference = tds.get_conference(gender, division, name)

            return conference
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )


commits_club_parser = ns.parser()
commits_club_parser.add_argument(
    "gender",
    type=str,
    location="args",
    choices=("all", "male", "female"),
    default="female",
)

commits_club_parser.add_argument(
    "year",
    type=str,
    location="args",
    choices=("2022", "2023", "2024", "2025"),
    default="2023",
)

commits_parser = ns.parser()
commits_parser.add_argument(
    "gender",
    type=str,
    location="args",
    choices=("all", "male", "female"),
    default="female",
)
commits_parser.add_argument(
    "division",
    type=str,
    location="args",
    choices=("di", "dii", "diii", "naia", "njcaa"),
    default="di",
)
commits_parser.add_argument("name", type=str, location="args", default="West Coast")
commits_parser.add_argument(
    "year",
    type=str,
    location="args",
    choices=("2023", "2024", "2025", "2026"),
    default="2023",
)


@ns.route(
    "/college/conference/commits/<string:gender>/<string:division>/<string:name>/<int:year>"
)
@ns.expect(commits_parser)
class ConferenceCommits(Resource):
    @ns.doc("get_conference_commits")
    @ns.response(HTTPStatus.OK.value, "Get the conference commits", school_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Commitments not found")
    @ns.marshal_list_with(school_model)
    def get(self, gender: str, division: str, name: str, year: int):
        """Get a conferences commitments"""
        try:
            schools = topdrawer.get_conference_commits(gender, division, name, year)

            return schools
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )


@ns.route("/college/commits/club/<string:gender>/<int:year>")
@ns.expect(commits_club_parser)
class ConferenceCommitsByClub(Resource):
    @ns.doc("get_conference_commits_club")
    @ns.response(HTTPStatus.OK.value, "Get commitments data for clubs", conference_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Commitments not found")
    @ns.marshal_list_with(commitments_by_club_model)
    def get(self, gender: str, year: int):
        """Get a commitment data for clubs"""
        try:
            return topdrawer.get_commitments_by_club(gender, year)
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )

college_details_parser = reqparse.RequestParser(bundle_errors=True)

college_details_parser.add_argument("name", type=str, location="args", default="Jacksonville State")
college_details_parser.add_argument(
    "gender",
    type=str,
    location="args",
    choices=("Male", "Female"),
    default="Female",
    help='Bad choice: {error_msg}'
)
college_details_parser.add_argument("clgid", type=int, location="args", default=258)

college_details_model = ns.model(
    "College Details",
    {
        "conference": fields.String(required=True, description="The conference name"),
        "conferenceUrl": fields.String(required=True, description="The conference url"),
        "nickname": fields.String(required=True, description="The schools nickname"),
        "state": fields.String(required=True, description="The schools state"),
        "city": fields.String(required=True, description="The schools city"),
        "enrollment": fields.Integer(required=True, description="The schools enrollment"),
        "coach": fields.String(required=True, description="The coaches name"),
        "phone": fields.String(required=True, description="The phone number")
    }
)

@ns.route("/college/details/<string:gender>/<string:name>/<int:clgid>")
@ns.expect(college_details_parser)
class CollegeDetails(Resource):
    @ns.doc("get_college_details")
    @ns.response(HTTPStatus.OK.value, "Get college details", college_details_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Details not found")
    @ns.marshal_with(college_details_model)
    def get(self, gender: str, name: str, clgid: int):
        """Get a colleges details"""
        try:
            return topdrawer.get_college_details(gender, name, clgid)
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )

conference_details_parser = reqparse.RequestParser(bundle_errors=True)

conference_details_parser.add_argument(
    "gender",
    type=str,
    location="args",
    choices=("Male", "Female"),
    default="Female",
    help='Bad choice: {error_msg}'
)
conference_details_parser.add_argument("name", type=str, location="args", default="Atlantic Coast")
conference_details_parser.add_argument("cfid", type=int, location="args", default=3)

@ns.route("/college/conference/details/<string:gender>/<string:name>/<int:cfid>")
@ns.expect(conference_details_parser)
class ConferenceDetails(Resource):
    @ns.doc("get_conference_details")
    @ns.response(HTTPStatus.OK.value, "Get conference details", school_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Details not found")
    @ns.marshal_list_with(school_model)
    def get(self, gender: str, name: str, cfid: int):
        """Get a conferences details"""
        try:
            return topdrawer.get_conference_details(gender, name, cfid)
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )

commitment_chart_data_model = ns.model(
    "Commitment Chart Data",
    {
        "name": fields.String(required=True, description="The display name of the pie slice"),
        "league": fields.String(required=True, description="The name of the league"),
        "value": fields.Integer(required=True, description="The number of players matching the league")
    }
)

@ns.route("/college/conference/commits/chart/data/<string:gender>/<string:name>/<int:cfid>/<int:year>")
@ns.param("gender", "The target gender", choices=("Male", "Female"), type=str, default="Female")
@ns.param("name", "The name of the conference", type=str, default="ASUN")
@ns.param("cfid", "The TopDrawerSoccer identifier of the conference", type=int, default=22)
@ns.param("year", "The graduation year", choices=(2022,2023,2024,2025), type=int, default=2023)
class ConferenceCommitmentsChartData(Resource):
    @ns.doc("get_conference_commitments_chart_data")
    @ns.response(HTTPStatus.OK.value, "Get conference commitments chart data", commitment_chart_data_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Details not found")
    @ns.marshal_list_with(commitment_chart_data_model)
    def get(self, gender: str, name: str, cfid: int, year: int):
        """Get a conference commitment chart data"""
        try:
            return topdrawer.get_conference_commitment_chart_data(gender, name, cfid, year)
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )


@ns.route("/player/details/<string:name>/<int:pid>")
@ns.param("name", "The name of the target conference", type=str, default="Olivia Shippee")
@ns.param("pid", "The TopDrawerSoccer identifier of the player", type=int, default=150942)
class PlayerDetails(Resource):
    @ns.doc("get_player_details")
    @ns.response(HTTPStatus.OK.value, "Get player details", player_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Details not found")
    @ns.marshal_with(player_model)
    def get(self, name: str, pid: int):
        """Get a players details"""
        try:
            return topdrawer.get_player_details(name, pid)
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )
