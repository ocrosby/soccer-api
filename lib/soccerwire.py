import pprint
from urllib.error import HTTPError
import requests

from bs4 import BeautifulSoup

def get_commitments():
    """Retrieve commitments from SoccerWire"""
    pass

class SoccerWireController:
    def __init__(self):
        """Something"""
        pass

    def get_url(self, gender, year):
        if gender == "male":
            if year == "2020":
                return "https://www.soccerwire.com/recruiting/boys-2020"
            elif year == "2022":
                return "https://www.soccerwire.com/recruiting/boys-2022-college-commitments/?filter=eyJzb3J0X2J5IjoibWV0YS5pc19mZWF0dXJlZC5yYXciLCJzb3J0X2RpcmVjdGlvbiI6ImRlc2MiLCJxdWVyeSI6IiIsInNlbGVjdGVkRmlsdGVycyI6eyJtZXRhLmdlbmRlci5yYXciOiJtYWxlIiwibWV0YS5ncmFkdWF0aW9uX3llYXIucmF3IjoiMjAyMiIsIm1ldGEuaXNfY29tbWl0dGVkLnJhdyI6IjEifSwic2VsZWN0ZWRSYW5nZUZpbHRlcnMiOnt9LCJjdXJyZW50UGFnZSI6MX0="
            else:
                return f"https://www.soccerwire.com/boys-{year}-college-commitments"
        elif gender == "female":
            if year == "2020":
                return "https://www.soccerwire.com/recruiting/girls-2020-college-commitments"
            elif year == "2021":
                return "https://www.soccerwire.com/recruiting/girls-2021-college-commitments"
            else:
                return f"https://www.soccerwire.com/girls-{year}-college-commitments"
        else:
            return None


    def commitments(self, gender, year, team=None, club=None, positions=None, state=None):
        url = self.get_url(gender, year)

        response = requests.get(url)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", {"id": "players__table"})
        body = table.find("tbody")
        rows = body.find_all("tr")

        if table is None:
            print("Unable to locate the table")



        print(f"Gender {gender}")
        print(f"Year {year}")
        print(f"Team {team}")
        print(f"Club {club}")
        print(f"Positions {positions}")
        print(f"State {state}")

        return []


if __name__ == "__main__":
    controller = SoccerWireController()

    commitments = controller.commitments(gender='female', year='2023')

    for player in commitments:
        pprint(player)

