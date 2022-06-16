import requests

from flask import jsonify
from flask_restx import Namespace, Resource, fields

ns = Namespace('ecnl', description='ECNL related operations')

club = ns.model('Club', {
    'id': fields.Integer(required=True, description='The club identifier'),
    'orgId': fields.Integer(required=True, description='The organization identifier'),
    'name': fields.String(required=True, description='The club name'),
    'city': fields.String(required=True, description='The club city'),
    'state': fields.String(required=True, description='the club state')
})

@ns.route('/clubs')
class ClubList(Resource):
    @ns.doc('list_clubs')
    @ns.marshal_list_with(club)
    def get(self):
        '''List all clubs'''
        url = "https://api.totalglobalsports.com/json/?token=Q0jcEIroy7Y=|9&ds=GetOrgClublistBySeasonIDPagingSP&oid=9&orgsid=12"

        page = requests.get(url)

        return jsonify(page.json())
