from pprint import pprint

import requests

from bs4 import BeautifulSoup

#from common.extensions import cache

URLS = {
    'home': 'https://usclubsoccer.org/npl-member-leagues/'
}

#@cache.memoize(timeout=604800) # 1 week (it shouldn't change frequently)
def get_member_leagues():
    """Returns all the member leagues from the NPL"""
    member_leagues = []

    response = requests.get(URLS['home'])

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    nav = soup.find(id="children-nav")
    items = nav.find_all('li', class_=["page_item"])

    for item in items:
        anchor = item.find('a')
        if anchor is not None:
            url = anchor["href"]
        else:
            url = None

        member_leagues.append({
            "name": item.text.strip(),
            "url": url
        })

    return member_leagues

#@cache.memoize(timeout=300) # 5 min
def get_member_league_by_name(league_name: str):
    """Returns a member league dict by league name."""
    member_leagues = get_member_leagues()

    for league in member_leagues:
        if league["name"] == league_name:
            return league

    return None

#@cache.memoize(timeout=300) # 5 min
def get_clubs_by_league_name(league_name: str, gender: str = None):
    league = get_member_league_by_name(league_name)

    if league is None:
        return None

    response = requests.get(league["url"])

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    container = soup.find('div', { "data-widget_type": "text-editor.default" })

    clubs = []
    if container is not None:
        if league["name"] == "SOCAL Discovery NPL":
            response = requests.get("https://elements.demosphere.com/73496/teams/club/List.html?rand6=339879#is_embedded=true")

            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("table", {"id": "cb-list-tbl-1"})
            cells = table.find_all("td")

            for cell in cells:
                name = cell.text.strip()
                anchor = cell.find("a")
                if anchor is not None:
                    url = "https://elements.demosphere.com" + anchor["href"]
                else:
                    url = None

                clubs.append({"name": name, "url": url})
        elif league["name"] in ["South Atlantic Premier League"]:
            # These use Boys and Girls lists.
            parent = container.find('div', class_=["elementor-widget-container"])
            children = parent.findChildren()

            if gender.strip().lower() == "male":
                # Extract male clubs.
                target = -1
                for i in range(0, len(children)):
                    child = children[i]
                    if child.text.strip() == "Boys clubs:":
                        target = i
                        break

                items = children[target+1].find_all("li")
                for item in items:
                    name = item.text.strip()
                    anchor = item.find("a")
                    if anchor is not None:
                        url = anchor["href"]
                    else:
                        url = None

                    clubs.append({"name": name, "url": url})

            elif gender.strip().lower() == "female":
                # Extract female clubs.
                target = -1
                for i in range(0, len(children)):
                    child = children[i]
                    if child.text.strip() == "Girls clubs:":
                        target = i
                        break

                items = children[target+1].find_all("li")
                for item in items:
                    name = item.text.strip()
                    anchor = item.find("a")
                    if anchor is not None:
                        url = anchor["href"]
                    else:
                        url = None

                    clubs.append({"name": name, "url": url})
            else:
                # The gender is invalid.
                raise Exception(f"Invalid gender specified {gender}!  Expected ('male'|'female')")

        elif league["name"] in ["USC Champions League"]:
            # These use a table instead of a list.
            pass
        else:
            # Assume it has leagues with very simple uniform lists.
            items = container.find_all("li")
            for item in items:
                name = item.text.strip()
                anchor = item.find("a")
                if anchor is not None:
                    url = anchor["href"]
                else:
                    url = None

                clubs.append({"name": name, "url": url})

    return clubs

if __name__ == "__main__":
    member_leagues = get_member_leagues()

    good_leagues = []
    bad_leagues = []

    for league in member_leagues:
        print("--------------------------------------------------------------------------------")
        print(league)
        league_name = league["name"]

        print(f"Attempting to load '{league_name}' ...")
        clubs = get_clubs_by_league_name(league_name, "female")

        if len(clubs) > 0:
            good_leagues.append(league_name)
            print(f"\nThere are {len(clubs)} clubs in '{league_name}'.")
        else:
            bad_leagues.append(league_name)
            print(f"\nI'm having trouble extracting clubs for '{league_name}'.")

    print()
    print("Good:")
    for league in good_leagues:
        print(f"\t{league}")

    print()
    print("Bad:")
    for league in bad_leagues:
        print(f"\t{league}")

    print()
    if len(bad_leagues) == 0:
        print("You are good to go!")
    else:
        print("You still have some work to do!")
