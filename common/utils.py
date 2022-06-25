import requests

from bs4 import BeautifulSoup

division_mapping = {
    "di": "/di/divisionid-1",
    "dii": "/dii/divisionid-2",
    "diii": "/diii/divisionid-3",
    "naia": "/naia/divisionid-4",
    "njcaa": "/njcaa/divisionid-5"
}

class TopDrawerSoccer:
    def __init__(self):
        """Constructor"""
        pass

    def get_conference_commits(self, gender: str, division: str, name: str):
        conference = self.get_conference(gender, division, name)

        url = conference['url'] + "/tab-commitments#commitments"

        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")

        tables = soup.find_all("table", class_=["table-striped", "tds-table", "female"])

        body = None
        for table in tables:
            header = table.find("thead", class_="female")
            if header is not None:
                body = table.find("tbody")

        schools = []
        if body is not None:
            rows = body.find_all("tr")

            for row in rows:
                columns = row.find_all("td")
                if len(columns) == 1:
                    name = columns[0].text.strip()
                    school = { "name": name, "players": [] }
                    schools.append(school)
                else:
                    player = { "name": None, "year": None, "position": None, "city": None, "state": None, "club": None }
                    player["name"] = columns[0].text.strip()
                    player["year"] = columns[1].text.strip()
                    player["position"] = columns[2].text.strip()
                    player["city"] = columns[3].text.strip()
                    player["state"] = columns[4].text.strip()
                    player["club"] = columns[5].text.strip()

                    school["players"].append(player)

        return schools


    def get_conference(self, gender: str, division: str, name: str):
        conferences = self.get_conferences(gender, division)

        for conference in conferences:
            if conference['name'] == name:
                return conference

        return None

    def get_conferences(self, gender: str, division: str):
        url = "https://www.topdrawersoccer.com/college-soccer/college-conferences"

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

                conference_id = int(url.split('/')[-1].split('-')[-1])

                # schools = self.get_conference_commits(gender, division, name)
                schools = None

                if gender == "male" and "Men's" in heading:
                    conferences.append({ "id": conference_id, "name": name, "url": url, "schools": schools})

                if gender == "female" and "Women's" in heading:
                    conferences.append({ "id": conference_id, "name": name, "url": url, "schools": schools})

        return conferences
