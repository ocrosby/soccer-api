from flask import Blueprint
from flask_restx import Api

from .ecnl import ns as ns1

blueprint = Blueprint('api', __name__, url_prefix='/api/1')

api = Api(blueprint,
          title='Soccer APIs',
          version='1.0',
          description='API endpoints for Soccer data retrieval'
          )

api.add_namespace(ns1, path='/api/ecnl')
