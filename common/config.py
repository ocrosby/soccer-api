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

GA_CLUBS = load_ga_clubs("data/ga_clubs.json")
CLUB_TRANSLATIONS = load_club_translations("data/club_translations.json")

if __name__ == "__main__":
    print(GA_CLUBS)
