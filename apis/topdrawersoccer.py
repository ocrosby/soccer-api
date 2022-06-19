import requests

from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from http import HTTPStatus
from flask import jsonify
from flask_restx import Namespace, Resource, fields

ns = Namespace('tds', description='TopDrawerSoccer related operations')

conference_model = ns.model('Conference', {
    'id': fields.Integer(required=True, description='The identifier of the conference.'),
    'name': fields.String(required=True, description='The conference name'),
    'url': fields.String(required=True, description='The conference url')
})

# /college/conferences/<gender:string>
# /college/teams/<gender:string>
# /college/commitments/<gender:string>,<year:int>
# /college/commitments/conference/<gender:string>,<year:int>

# /college/conference/details/<name:string>

division_mapping = {
    "di": "/di/divisionid-1",
    "dii": "/dii/divisionid-2",
    "diii": "/diii/divisionid-3",
    "naia": "/naia/divisionid-4",
    "njcaa": "/njcaa/divisionid-5"
}

@ns.route('/college/conferences/<string:gender>/<string:division>')
@ns.param('gender', 'The target gender [male|female]')
@ns.param('division', 'The target division [di|dii|diii|naia|njcaa] (defaults to di)')
class ClubList(Resource):
    @ns.doc('list_conferences')
    @ns.response(HTTPStatus.OK.value, "Get the item list", [conference_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(conference_model)
    def get(self, gender: str, division: str):
        '''List all conferences'''

        url = "https://www.topdrawersoccer.com/college-soccer/college-conferences"

        try:
            suffix = ""
            if division in division_mapping:
                suffix = division_mapping[division]

            response = requests.get(url + suffix)

            response.raise_for_status()

            conferences = []

            soup = BeautifulSoup(response.content, "html.parser")

            column_elements = soup.find_all("div", class_="col-lg-6")

            for column_element in column_elements:
                heading_element = column_element.find("div", class_="heading-rectangle")
                heading = heading_element.text.strip()

                table = column_element.find("table", class_=["table_striped", "tds_table"])

                if table is None:
                    continue

                cells = table.find_all("td")

                for cell in cells:
                    url = "https://www.topdrawersoccer.com" + cell.find("a")["href"]
                    name = cell.text.strip()
                    id = int(url.split('/')[-1].split('-')[-1])

                    if gender == "male" and "Men's" in heading:
                        conferences.append({ "id": id, "name": name, "url": url})

                    if gender == "female" and "Women's" in heading:
                        conferences.append({ "id": id, "name": name, "url": url})

            return conferences
        except HTTPError as http_err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}")
        except Exception as err:
            return ns.abort(HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}")
