import json
import os
import flask

import public_links

app = flask.Flask(__name__)

app.register_blueprint(public_links.app)

@app.route('/')
def index():
    return flask.make_response('<h1>Codebase Public Links</h1>', 200)

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
