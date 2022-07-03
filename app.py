from flask import Flask
from flask_cors import CORS
from flask_healthz import healthz
from apis import blueprint as api


app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(healthz, url_prefix="/healthz")
CORS(app)

if __name__ == '__main__':
    app.run()
