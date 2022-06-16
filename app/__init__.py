from flask import Flask
from flask_restx import Api
from config import DevelopmentConfig

def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    api = Api(app, version='1.0', title='Soccer API', description='A simple API to consolidate Soccer data.')

    app.config.from_object(config)

    return app
