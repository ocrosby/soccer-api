from flask import Flask
from flask_cors import CORS
from apis import blueprint as api

app = Flask(__name__)
app.register_blueprint(api)
CORS(app)

if __name__ == '__main__':
    app.run()
