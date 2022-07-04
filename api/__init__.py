from flask import Flask, Blueprint
from flask_restx import Api
from flask_cors import CORS
from flask_healthz import healthz

from .ecnl import ns as ecnl
from .tds import ns as tds
from .ncaa import ns as ncaa

blueprint = Blueprint('api', __name__, url_prefix='/api')

api = Api(blueprint,
          title='Soccer APIs',
          version='1.0',
          description='API endpoints for Soccer data retrieval'
          )

api.add_namespace(ecnl, path='/ecnl')
api.add_namespace(tds, path='/tds')
api.add_namespace(ncaa, path='/ncaa')

app = Flask(__name__)
app.register_blueprint(blueprint)
app.register_blueprint(healthz, url_prefix="/healthz")
CORS(app)
