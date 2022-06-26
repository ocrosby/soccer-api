import requests

from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from http import HTTPStatus
from flask import jsonify
from flask_restx import Namespace, Resource, fields, reqparse

from common import utils


ns = Namespace('tds', description='TopDrawerSoccer related operations')

college_organization_model = ns.model('Organization', {
    'id': fields.String(required=True, description='The organization identifier'),
    'name': fields.String(required=True, description='The organization name')
})

college_division_model = ns.model('Division', {
    'divisionId': fields.String(required=True, description='The division identifier'),
    'divisionName': fields.String(required=True, description='The division name'),
    'orgId': fields.String(required=True, description='The organization identifier')
})

player_model = ns.model('Player', {
    'name': fields.String(required=True, description='The player name'),
    'year': fields.String(required=True, description='The players graduation year'),
    'position': fields.String(required=True, description='The players position'),
    'city': fields.String(required=True, description='The players home city'),
    'state': fields.String(required=True, description='The players home state'),
    'club': fields.String(required=True, description='The players club')
})

school_model = ns.model('School', {
    'name': fields.String(required=True, description='The school name'),
    'players': fields.List(fields.Nested(player_model))
})

conference_model = ns.model('Conference', {
    'id': fields.Integer(required=True, description='The identifier of the conference.'),
    'name': fields.String(required=True, description='The conference name'),
    'url': fields.String(required=True, description='The conference url'),
    'schools': fields.List(fields.Nested(school_model))
})

# /college/conferences/<gender:string>
# /college/teams/<gender:string>
# /college/commitments/<gender:string>,<year:int>
# /college/commitments/conference/<gender:string>,<year:int>

# /college/conference/details/<name:string>

tgs = utils.TopDrawerSoccer()

gender_parser = reqparse.RequestParser()
gender_parser.add_argument('gender', type=str, choices=("male", "female"))

division_parser = reqparse.RequestParser()
division_parser.add_argument('division', type=str, choices=("di", "dii", "diii", "naia", "njcaa"))

COLLEGE_ORGANIZATIONS = [
    {"id": "ncaa", "name": "National Collegiate Athletic Association"},
    {"id": "naia", "name": "National Association of Intercollegiate Athletics"},
    {"id": "njcaa", "name": "National Junior College Athletic Association"}
]
@ns.route('/college/organizations')
class CollegeOrganizations(Resource):
    @ns.doc('list_college_organizations')
    @ns.response(HTTPStatus.OK.value, "Get the organization list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(college_organization_model)
    def get(self):
        '''List all college organizations'''
        return COLLEGE_ORGANIZATIONS

COLLEGE_DIVISIONS = [
    {"divisionId": 1, "divisionName": "di", "orgId": "ncaa"},
    {"divisionId": 2, "divisionName": "dii", "orgId": "ncaa"},
    {"divisionId": 3, "divisionName": "diii", "orgId": "ncaa"},
    {"divisionId": 4, "divisionName": "naia", "orgId": "naia"},
    {"divisionId": 5, "divisionName": "njcaa", "orgId": "njcaa"}
]

@ns.route('/college/divisions')
class CollegeOrganizations(Resource):
    @ns.doc('list_college_divisions')
    @ns.response(HTTPStatus.OK.value, "Get the division list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(college_division_model)
    def get(self):
        '''List all college divisions'''
        return COLLEGE_DIVISIONS




@ns.route('/college/conferences/<string:gender>/<string:division>')
@ns.expect(gender_parser)
@ns.expect(division_parser)
class ClubList(Resource):
    @ns.doc('list_conferences')
    @ns.response(HTTPStatus.OK.value, "Get the item list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(conference_model)
    def get(self, gender: str, division: str):
        '''List all conferences'''
        try:
            return tgs.get_conferences(gender, division)
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")

@ns.route('/college/conference/<string:gender>/<string:division>/<string:name>')
@ns.param('gender', 'The gender of the target conference')
@ns.param('division', 'The division of the target conference')
@ns.param('name', 'The name of the target conference')
class Conference(Resource):
    @ns.doc('get_conference')
    @ns.response(HTTPStatus.OK.value, "Get the conference", conference_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Conference not found")
    @ns.marshal_with(conference_model)
    def get(self, gender: str, division: str, name: str):
        '''Get a conference by name'''
        try:
            conference = tgs.get_conference(gender, division, name)

            return conference
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")

@ns.route('/college/conference/commits/<string:gender>/<string:division>/<string:name>/<int:year>')
@ns.param('gender', 'The gender of the target conference')
@ns.param('division', 'The division of the target conference')
@ns.param('name', 'The name of the target conference')
@ns.param('year', 'The graduation year of the commits')
class ConferenceCommits(Resource):
    @ns.doc('get_conference')
    @ns.response(HTTPStatus.OK.value, "Get the conference", conference_model)
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Conference not found")
    @ns.marshal_list_with(school_model)
    def get(self, gender: str, division: str, name: str, year: int):
        '''Get a conferences commitments'''
        try:
            schools = tgs.get_conference_commits(gender, division, name, year)

            return schools
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")
