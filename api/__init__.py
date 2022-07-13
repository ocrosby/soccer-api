from flask import Blueprint, Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_healthz import healthz
from flask_restx import Api

from .ecnl import ns as ecnl
from .ncaa import ns as ncaa
from .tds import ns as tds
from .ga import ns as ga
from .club import ns as club

blueprint = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    blueprint,
    title="Soccer APIs",
    version="1.0",
    description="API endpoints for Soccer data retrieval",
)

api.add_namespace(ecnl, path="/ecnl")
api.add_namespace(tds, path="/tds")
api.add_namespace(ncaa, path="/ncaa")
api.add_namespace(ga, path="/ga")
api.add_namespace(club, path="/club")

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)

# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)

app.register_blueprint(blueprint)
app.register_blueprint(healthz, url_prefix="/healthz")

CORS(app)
