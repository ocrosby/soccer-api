# import the create app application factory
from app import create_app

# import the application config classes
from config import DevelopmentConfig, ProductionConfig, TestingConfig

import requests
from flask import jsonify, request

app = create_app()

COLLEGE_ORGANIZATIONS = [
    {"id": "ncaa", "name": "National Collegiate Athletic Association"},
    {"id": "naia", "name": "National Association of Intercollegiate Athletics"},
    {"id": "njcaa", "name": "National Junior College Athletic Association"}
]

COLLEGE_DIVISIONS = [
    {"divisionId": 1, "divisionName": "di", "orgId": "NCAA"},
    {"divisionId": 2, "divisionName": "dii", "orgId": "NCAA"},
    {"divisionId": 3, "divisionName": "diii", "orgId": "NCAA"},
    {"divisionId": 4, "divisionName": "naia", "orgId": "NAIA"},
    {"divisionId": 5, "divisionName": "njcaa", "orgId": "NJCAA"}
]


@app.route("/api/ecnl/clubs")
def ecnl_clubs():
    url = "https://api.totalglobalsports.com/json/?token=Q0jcEIroy7Y=|9&ds=GetOrgClublistBySeasonIDPagingSP&oid=9&orgsid=12"

    page = requests.get(url)

    return jsonify(page.json())


@app.route("/api/college/organizations")
def college_organizations():
    return jsonify({"data": COLLEGE_ORGANIZATIONS})


@app.route("/api/college/divisions")
def college_divisions():
    return jsonify({"data": COLLEGE_DIVISIONS})


def lookup_division_id_by_name(name):
       for division in COLLEGE_DIVISIONS:
              if division.divisionName == name:
                     return division.id

       return None

def parse_conference_table(table):
       pass

@app.route("/api/college/soccer/conferences/<divisionName>/gender")
def college_soccer_conferences(divisionName, gender):
       division_id = lookup_division_id_by_name(divisionName)
       url = "https://www.topdrawersoccer.com/college-soccer/college-conferences/dii/divisionid-" + division_id

       page = requests.get(url)
       soup = BeautifulSoup(page.content, "html.parser")
       columns = soup.find_all("div", class_="col-lg-6")

       for column in columns:
              heading = column.find("div", class_="heading-rectangle").text.strip()
              conferences = []

              # Parse the conferences
              table = column.find("table", class_=["table-striped", "tds-table", "male"])

              if gender == "male" and heading == "Men's College Conferences":
                     return parse_conference_table(table)
                     

              if gender == "female" and heading == "Women's College Conferences":
                      return parse_conference_table(table)

              continue
                     
       

    return None