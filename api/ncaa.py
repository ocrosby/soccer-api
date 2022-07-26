from http import HTTPStatus

from flask_restx import Namespace, Resource, fields
from requests.exceptions import HTTPError

from lib import ncaa as library

ns = Namespace("ncaa", description="NCAA related operations")

ncaa_coaches_di_ranking_model = ns.model(
    "CoachesRanking",
    {
        "rank": fields.Integer(
            required=True, description="The coaches ranking of the school"
        ),
        "school": fields.String(required=True, description="The name of the school"),
        "points": fields.Integer(
            required=True, description="The points for the school"
        ),
        "record": fields.String(required=True, description="The record of the school"),
        "previous": fields.String(
            required=True, description="The previous rank of the school"
        ),
    },
)

ncaa_coaches_dii_ranking_model = ns.model(
    "CoachesRanking",
    {
        "rank": fields.Integer(required=True, description="The ranking of the school"),
        "school": fields.String(required=True, description="The name of the school"),
        "previous": fields.String(
            required=True, description="The previous rank of the school"
        ),
        "record": fields.String(required=True, description="The record of the school"),
    },
)

ncaa_rpi_ranking_model = ns.model(
    "RPIRanking",
    {
        "rank": fields.Integer(required=True, description="The ranking of the school"),
        "school": fields.String(required=True, description="The name of the school"),
        "conference": fields.String(
            required=True, description="The conference of the school"
        ),
        "record": fields.String(required=True, description="The record of the school"),
        "neutral": fields.String(
            required=True, description="The neutral record of the school"
        ),
        "non-div-i": fields.String(required=True, description=""),
    }
)

ncaa_school_model = ns.model(
    "NCAASchool",
    {
        "name": fields.String(required=True, description="The official name of the school"),
        "conference": fields.String(required=True, description="The name of the conference"),
        "private": fields.String(required=True, description="Is it private?"),
        "hbcu": fields.String(required=True, description="Is it an HBCU?"),
        "state": fields.String(required=True, description="The state it's in.")
    }
)

@ns.route("/rankings/dii/united-soccer-coaches")
class NCAAUnitedSoccerCoachesD2RankingList(Resource):
    @ns.doc("list_ncaa_coaches_dii_rankings")
    @ns.response(
        HTTPStatus.OK.value,
        "Get the list of United Soccer Coaches DII rankings",
        [ncaa_coaches_di_ranking_model],
    )
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(ncaa_coaches_dii_ranking_model)
    def get(self):
        """List all United Soccer Coaches DII rankings"""
        try:
            return library.get_usc_d2_rankings()
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )

@ns.route("/rankings/di/united-soccer-coaches")
class NCAAUnitedSoccerCoachesD1RankingList(Resource):
    @ns.doc("list_ncaa_coaches_di_rankings")
    @ns.response(
        HTTPStatus.OK.value,
        "Get the list of United Soccer Coaches DI rankings",
        [ncaa_coaches_di_ranking_model],
    )
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(ncaa_coaches_di_ranking_model)
    def get(self):
        """List all United Soccer Coaches DI rankings"""
        try:
            return library.get_usc_d1_rankings()
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )


@ns.route("/rankings/di/rpi")
class NCAARPIRankingList(Resource):
    @ns.doc("list_ncaa_rpi_rankings")
    @ns.response(
        HTTPStatus.OK.value, "Get the list of RPI rankings", [ncaa_rpi_ranking_model]
    )
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(ncaa_rpi_ranking_model)
    def get(self):
        """List all RPI rankings"""
        try:
            return library.get_rpi_rankings()
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )

@ns.route('/schools/<division>')
class NCAASchoolList(Resource):
    @ns.doc("list_ncaa_rpi_rankings")
    @ns.response(
        HTTPStatus.OK.value, "Get the list of NCAA schools", [ncaa_school_model]
    )
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(ncaa_school_model)
    def get(self, division: str):
        """List all NCAA schools of the specified division"""
        try:
            return library.get_schools(division)
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )
