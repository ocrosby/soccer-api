import json

def load_club_translations(path: str):
    translations = {}

    f = open(path)
    container = json.load(f)

    for translation in container["data"]:
        translations[translation["from"]] = translation["to"]

    f.close()

    return translations

def load_ga_clubs(path: str):
    f = open(path)
    container = json.load(f)

    clubs = container["data"]

    f.close()

    return clubs

def translate_club_name(club_name: str):
    if club_name is None:
        return None

    club_name = club_name.strip()

    if len(club_name) == 0:
        return ''

    if club_name in CLUB_TRANSLATIONS:
        club_name = CLUB_TRANSLATIONS[club_name]

    return club_name

GA_CLUBS = load_ga_clubs("data/ga_clubs.json")
CLUB_TRANSLATIONS = load_club_translations("data/club_translations.json")

DIVISION_MAPPING = {
    "di": "/di/divisionid-1",
    "dii": "/dii/divisionid-2",
    "diii": "/diii/divisionid-3",
    "naia": "/naia/divisionid-4",
    "njcaa": "/njcaa/divisionid-5"
}

COLLEGE_ORGANIZATIONS = [
    {"id": "ncaa", "name": "National Collegiate Athletic Association"},
    {"id": "naia", "name": "National Association of Intercollegiate Athletics"},
    {"id": "njcaa", "name": "National Junior College Athletic Association"},
]

COLLEGE_DIVISIONS = [
    {"divisionId": 1, "divisionName": "di", "orgId": "ncaa"},
    {"divisionId": 2, "divisionName": "dii", "orgId": "ncaa"},
    {"divisionId": 3, "divisionName": "diii", "orgId": "ncaa"},
    {"divisionId": 4, "divisionName": "naia", "orgId": "naia"},
    {"divisionId": 5, "divisionName": "njcaa", "orgId": "njcaa"},
]

DIVISION_MAPPING = {
    "di": "/di/divisionid-1",
    "dii": "/dii/divisionid-2",
    "diii": "/diii/divisionid-3",
    "naia": "/naia/divisionid-4",
    "njcaa": "/njcaa/divisionid-5"
}

POSITION_LOOKUP = {
    "All": 0,
    "Goalkeeper": 1,
    "Defender": 2,
    "Midfielder": 6,
    "Forward": 5
}

REGION_LOOKUP = {
    "All": 0,
    "Florida": 10,
    "Great Lakes": 7,
    "Heartland": 5,
    "International": 17,
    "Mid Atlantic": 100,  # or possibly 12
    "Midwest": 6,
    "New Jersey": 14,
    "New York": 15,
    "Northeast": 16,
    "Northern California & Hawaii": 2,
    "Pacific Northwest": 3,
    "Pennsylvania": 13,
    "Rocky Mountains & Southwest": 4,
    "South": 9,
    "South Atlantic": 11,
    "Southern California": 1,
    "Texas": 8
}

STATE_LOOKUP = {
    "All": 0,
    "Alabama": 1,
    "Alaska": 2,
    "Arizona": 3,
    "Arkansas": 4,
    "California": 5,
    "Colorado": 6,
    "Connecticut": 7,
    "Delaware": 8,
    "District of Columbia": 9,
    "Florida": 10,
    "Georgia": 11,
    "Hawaii": 12,
    "Idaho": 13,
    "Illinois": 14,
    "Indiana": 15,
    "International": 99,
    "Iowa": 16,
    "Kansas": 17,
    "Kentucky": 18,
    "Louisiana": 19,
    "Maine": 20,
    "Maryland": 21,
    "Massachusetts": 22,
    "Michigan": 23,
    "Minnesota": 24,
    "Mississippi": 25,
    "Missouri": 26,
    "Montana": 27,
    "Nebraska": 28,
    "Nevada": 29,
    "New Hampshire": 30,
    "New Jersey": 31,
    "New Mexico": 32,
    "New York": 33,
    "North Carolina": 34,
    "North Dakota": 35,
    "Ohio": 36,
    "Oklahoma": 37,
    "Oregon": 38,
    "Pennsylvania": 39,
    "Rhode Island": 40,
    "South Carolina": 41,
    "South Dakota": 42,
    "Tennessee": 43,
    "Texas": 44,
    "Utah": 45,
    "Vermont": 46,
    "Virginia": 47,
    "Washington": 48,
    "West Virginia": 49,
    "Wisconsin": 50,
    "Wyoming": 51
}


if __name__ == "__main__":
    print(GA_CLUBS)
