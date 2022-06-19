from flask import Blueprint
from flask_restx import Api

from .ecnl import ns as ecnl
from .topdrawersoccer import ns as topdrawersoccer

blueprint = Blueprint('api', __name__, url_prefix='/api')

api = Api(blueprint,
          title='Soccer APIs',
          version='1.0',
          description='API endpoints for Soccer data retrieval'
          )

api.add_namespace(ecnl, path='/ecnl')
api.add_namespace(topdrawersoccer, path='/tgs')
