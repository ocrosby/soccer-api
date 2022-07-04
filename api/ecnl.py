import requests

from requests.exceptions import HTTPError

from http import HTTPStatus
from flask import jsonify
from flask_restx import Namespace, Resource, fields

ns = Namespace('ecnl', description='ECNL related operations')

club_model = ns.model('Club', {
    'id': fields.Integer(required=True, description='The club identifier'),
    'orgId': fields.Integer(required=True, description='The organization identifier'),
    'name': fields.String(required=True, description='The club name'),
    'city': fields.String(required=True, description='The club city'),
    'state': fields.String(required=True, description='the club state'),
    'logo': fields.String(required=True, description='The URL for the club logo')
})

@ns.route('/clubs')
class ClubList(Resource):
    @ns.doc('list_clubs')
    @ns.response(HTTPStatus.OK.value, "Get the item list", [club_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(club_model)
    def get(self):
        '''List all clubs'''

        url = "https://public.totalglobalsports.com/api/Event/get-org-club-list-by-orgID/9"

        try:
            response = requests.get(url)

            response.raise_for_status()

            json_response = response.json()

            clubs = []

            for item in json_response["data"]:
                club = {}

                club["id"] = item["clubID"]
                club["orgId"] = item["orgID"]
                club["name"] = item["clubFullName"].strip()
                club["city"] = item["city"].strip()
                club["state"] = item["stateCode"].strip()
                club["logo"] = item["clubLogo"].strip()

                clubs.append(club)

            return clubs
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")
