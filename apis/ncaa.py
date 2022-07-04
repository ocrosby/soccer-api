import requests
from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from http import HTTPStatus
from flask import jsonify
from flask_restx import Namespace, Resource, fields

ns = Namespace('ncaa', description='NCAA related operations')

ncaa_coaches_di_ranking_model = ns.model('CoachesRanking', {
    'rank': fields.Integer(required=True, description='The coaches ranking of the school'),
    'school': fields.String(required=True, description='The name of the school'),
    'points': fields.Integer(required=True, description='The points for the school'),
    'record': fields.String(required=True, description='The record of the school'),
    'previous': fields.String(required=True, description='The previous rank of the school')
})

ncaa_coaches_dii_ranking_model = ns.model('CoachesRanking', {
    'rank': fields.Integer(required=True, description='The ranking of the school'),
    'school': fields.String(required=True, description='The name of the school'),
    'previous': fields.String(required=True, description='The previous rank of the school'),
    'record': fields.String(required=True, description='The record of the school')
})

ncaa_rpi_ranking_model = ns.model('RPIRanking', {
    'rank': fields.Integer(required=True, description='The ranking of the school'),
    'school': fields.String(required=True, description='The name of the school'),
    'conference': fields.String(required=True, description='The conference of the school'),
    'record': fields.String(required=True, description='The record of the school'),
    'neutral': fields.String(required=True, description='The neutral record of the school'),
    'non-div-i': fields.String(required=True, description='')
})

@ns.route('/rankings/dii/united-soccer-coaches')
class NCAAUnitedSoccerCoachesD2RankingList(Resource):
    @ns.doc('list_ncaa_coaches_dii_rankings')
    @ns.response(HTTPStatus.OK.value, "Get the list of United Soccer Coaches DII rankings", [ncaa_coaches_di_ranking_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(ncaa_coaches_dii_ranking_model)
    def get(self):
        '''List all United Soccer Coaches DII rankings'''

        url = "https://unitedsoccercoaches.org/rankings/college-rankings/ncaa-dii-women/"

        try:
            response = requests.get(url)

            response.raise_for_status()

            rankings = []

            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("table", class_="rankingsTable")
            body = table.find("tbody")
            rows = body.find_all("tr", recursive=False)

            for row in rows:
                cells = row.findChildren("td")
                ranking = {
                    "rank": int(cells[0].text.strip()),
                    "school": cells[1].text.strip(),
                    "previous": cells[2].text.strip(),
                    "record": cells[3].text.strip()
                }

                rankings.append(ranking)

            return rankings
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")


@ns.route('/rankings/di/united-soccer-coaches')
class NCAAUnitedSoccerCoachesD1RankingList(Resource):
    @ns.doc('list_ncaa_coaches_di_rankings')
    @ns.response(HTTPStatus.OK.value, "Get the list of United Soccer Coaches DI rankings", [ncaa_coaches_di_ranking_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(ncaa_coaches_di_ranking_model)
    def get(self):
        '''List all United Soccer Coaches DI rankings'''

        url = "https://www.ncaa.com/rankings/soccer-women/d1/united-soccer-coaches"

        try:
            response = requests.get(url)

            response.raise_for_status()

            rankings = []

            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("table")
            body = table.find("tbody")
            rows = body.find_all("tr", recursive=False)

            for row in rows:
                cells = row.findChildren("td")
                ranking = {
                    "rank": int(cells[0].text.strip()),
                    "school": cells[1].text.strip(),
                    "points": int(cells[2].text.strip()),
                    "record": cells[3].text.strip(),
                    "previous": cells[4].text.strip()
                }

                rankings.append(ranking)

            return rankings
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")

@ns.route('/rankings/di/rpi')
class NCAARPIRankingList(Resource):
    @ns.doc('list_ncaa_rpi_rankings')
    @ns.response(HTTPStatus.OK.value, "Get the list of RPI rankings", [ncaa_rpi_ranking_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(ncaa_rpi_ranking_model)
    def get(self):
        '''List all RPI rankings'''

        url = "https://www.ncaa.com/rankings/soccer-women/d1/ncaa-womens-soccer-rpi"

        try:
            response = requests.get(url)

            response.raise_for_status()

            rankings = []

            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("table")
            body = table.find("tbody")
            rows = body.find_all("tr", recursive=False)

            for row in rows:
                cells = row.findChildren("td")
                ranking = {
                    "rank": int(cells[0].text.strip()),
                    "school": cells[1].text.strip(),
                    "conference": cells[1].text.strip(),
                    "record": cells[2].text.strip(),
                    "neutral": cells[3].text.strip(),
                    "non-div-i": cells[4].text.strip()
                }

                rankings.append(ranking)

            return rankings
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")

