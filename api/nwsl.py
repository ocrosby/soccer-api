from http import HTTPStatus

import requests
from flask_restx import Namespace, Resource, fields
from requests.exceptions import HTTPError
from common import utils
from common.extensions import cache

ns = Namespace("nwsl", description="NWSL related operations")


team_history_model = ns.model(
    "Team History Model",
    {
        "seasonStartDate": fields.String(required=True, description="The start date of the season"),
        "seasonYear": fields.Integer(required=True, description="The year of the season"),
        "teamCode": fields.String(required=False, description="The code of the team"),
        "teamName": fields.String(required=False, description="The name of the team"),
        "tournamentId": fields.String(required=False, description="The id of the tournament")
    }
)

image_model = ns.model(
    "Image Model",
    {
        "alt_text": fields.String(required=True, description="The alternate text for the image"),
        "filename": fields.String(required=True, description="The image file name"),
        "id": fields.String(required=True, description="The image ID"),
        "path": fields.String(required=True, description="The path for the image"),
        "title": fields.String(required=True, description="The title of the image"),
        "url": fields.String(required=True, description="The URL of the image"),
    }
)

team_model = ns.model(
    "Team Model",
    {
        "abbreviation": fields.String(required=True, description="The team abbreviation"),
        #"athletics_website": fields.String(required=True, description="The team website"),
        #"banner_image": fields.Nested(image_model),
        #"contestant_id": fields.String(required=True, description="The team contestant identifier"),
        #"current_record": fields.String(required=True, description="The record of the team"),
        #"edu_website": fields.String(required=True, description="The website for their junk"),
        #"facebook_id": fields.String(required=True, description="The facebook id for the team"),
        #"facebook_page": fields.String(required=True, description="The facebook page for the team"),
        #"facebook_username": fields.String(required=True, description="The facebook username for the team"),
        #"gallery_id": fields.String(required=True, description="The teams gallery identifier"),
        "head_coach": fields.String(required=True, description="The head coach for the team"),
        "home_field": fields.String(required=True, description="The home field for the team"),
        "id": fields.String(required=True, description="The teams identifier"),
        #"image": fields.Nested(image_model),
        #"impact_image": fields.Nested(image_model),
        #"instagram_username": fields.String(required=True, description="The instagram username for the team"),
        "is_hidden": fields.Boolean(required=True, description="Is the team hidden"),
        #"lineup": fields.String(required=True, description="The lineup for the team"),
        #"links": fields.String(required=True, description="The links for the team"),
        "location": fields.String(required=True, description="The location of the team"),
        #"logo": fields.Nested(image_model),
        #"mascot": fields.String(required=True, description="The mascot for the team"),
        #"member_type": fields.String(required=True, description="The member type of the team"),
        # next_game: {date: "2022-07-16T20:30:00", opponent_id: "dzxypx8djih58p668surbi4qm",…}
        # primary_background: "#000"
        # primary_text: "#fff"
        # record: null
        # safe_text_black: "#fff"
        # safe_text_white: "#000"
        # schedule_display: "Houston Dash"
        # school_active: true
        #"shop_url": fields.String(required=True, description="The shopping URL for the team"),
        "short_display": fields.String(required=True, description="The short display name for the team"),
        "shortname": fields.String(required=True, description="The short name of the team"),
        "slug": fields.String(required=True, description="The slug of the team"),
        #"snapchat_username": fields.String(required=True, description="The snapchat username for the team"),
        # stats: null
        #"team_history": fields.List(fields.Nested(team_history_model)),
        #"title": fields.String(required=True, description="The title of the team"),
        #"twitter_username": fields.String(required=True, description="The Twitter username for the team"),
        "website_url": fields.String(required=True, description="The teams website URL"),
        #"youtube_username": fields.String(required=True, description="The YouTube username for the team"),
    }
)



player_model = ns.model(
    "NWSL Player",
    {
        "country": fields.String(required=False, description="The players country of origin"),
        "countryId": fields.String(required=True, description="The players country ID"),
        "dateOfBirth": fields.String(required=True, description="The players date of birth"),
        "firstName": fields.String(required=True, description="The players first name"),
        "height": fields.String(required=True, description="The players height"),
        "hometown": fields.String(required=True, description="The players hometown"),
        "id": fields.String(required=True, description="The players id"),
        "lastName": fields.String(required=True, description="The players last name"),
        "position": fields.String(required=True, description="The players position"),
        "shirtNumber": fields.String(required=True, description="The players jersey number"),
        "slug": fields.String(required=True, description="The players slug"),
        "team": fields.Nested(team_model)
    }
)

@ns.route("/players")
class ClubList(Resource):
    @ns.doc("player_list")
    @ns.response(HTTPStatus.OK.value, "Get the NWSL player list", [player_model])
    @ns.response(HTTPStatus.BAD_REQUEST.value, "Item not found")
    @ns.marshal_list_with(player_model)
    @cache.cached(timeout=604800)
    def get(self):
        """List all players"""

        url = "https://d2nkt8hgeld8zj.cloudfront.net/services/nwsl.ashx/players"

        try:
            response = requests.get(url)
            response.raise_for_status()

            json = response.json()

            return json["data"]
        except HTTPError as http_err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            return ns.abort(
                HTTPStatus.BAD_REQUEST.value, f"Other error occurred: {err}"
            )
