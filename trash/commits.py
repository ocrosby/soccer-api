import requests

from bs4 import BeautifulSoup

class Player:
    def __init__(self):
        self.name = None
        self.year = None
        self.position = None
        self.city = None
        self.state = None
        self.club = None

    def display(self):
        print("\t\t", self.name, self.year, self.position, self.city, self.state, self.club)

class School:
    def __init__(self, name):
        self.name = name
        self.players = []

    def get_players_by_year(self, target_year):
        selected_players = []

        for player in self.players:
            if player.year == target_year:
                selected_players.append(player)

        return selected_players

class Conference:
    def __init__(self, name, path):
        self.name = name.strip()
        self.path = path.strip()

    def display(self):
        print(self.name)
        #print(self.name, ",", self.path)

    def get_commit_table_body(self):
        # https://www.topdrawersoccer.com/college-soccer/college-conferences/conference-details/women/asun/cfid-22/tab-commitments#commitments
        url = "https://www.topdrawersoccer.com" + self.path + "/tab-commitments#commitments"

        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")
        tables = soup.find_all("table", class_=["table-striped", "tds-table", "female"])

        for table in tables:
            header = table.find("thead", class_="female")
            if header is not None:
                return table.find("tbody")

        return None

    def get_commits(self):
        body = self.get_commit_table_body()
        rows = body.find_all("tr")

        schools = {}

        for row in rows:
            columns = row.find_all("td")
            if len(columns) == 1:
                name = columns[0].text.strip()
                school = School(name)
                schools[name] = school
            else:
                player = Player()
                player.name = columns[0].text.strip()
                player.year = columns[1].text.strip()
                player.position = columns[2].text.strip()
                player.city = columns[3].text.strip()
                player.state = columns[4].text.strip()
                player.club = columns[5].text.strip()

                school.players.append(player)

        return schools

class ConferenceAgent:
    def __init__(self):
        self.url = "https://www.topdrawersoccer.com/college-soccer/teams/women"
        self.conferences = {}

    def load_conferences(self):
        page = requests.get(self.url)

        soup = BeautifulSoup(page.content, "html.parser")

        conference_elements = soup.find_all("table", class_=["table-striped", "tds-table", "female"])

        for conference_element in conference_elements:
            caption_element = conference_element.find("caption", class_="table-caption--top")
            link = caption_element.find("a")
            caption = caption_element.text.strip()

            self.conferences[caption] = Conference(caption, link["href"])

    def get_conferences(self):
        return self.conferences       


def display_commits():
    agent = ConferenceAgent()
    agent.load_conferences()
    conferences = agent.get_conferences()

    for conference_name in conferences:
        conference = conferences[conference_name]

        conference.display()
        schools = conference.get_commits()

        for school_name in schools:
            school = schools[school_name]

            commits = school.get_players_by_year("2023")
            
            print("\t", school_name, "[", len(commits), "]")
            for player in commits:
                player.display()

        print()

display_commits()