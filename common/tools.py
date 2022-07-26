from .utils import cache

def get_anchor_text(element):
    if element is None:
        return None

    anchor = element.find("a")

    if anchor is None:
        return element.text.strip()

    return anchor.text.strip()


def get_anchor_url(element, prefix = None):
    if element is None:
        return None

    anchor = element.find("a")

    if anchor is None:
        return None

    url = anchor["href"]
    url = url.strip()

    if len(url) == 0:
        return None

    if prefix is None:
        return url

    return prefix + url


def is_member_club(target_club_name: str, clubs: list):
    if target_club_name is None:
        return False

    if clubs is None:
        return False

    temp = target_club_name.strip().lower()

    if len(temp) == 0:
        return False

    for club in clubs:
        current_club_name = club["name"].strip().lower()

        if current_club_name == temp:
            return True

    return False
