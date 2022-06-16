from flask import Flask
from apis import blueprint as api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api/1')

if __name__ == '__main__':
    app.run()
