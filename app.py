from flask import Flask
from dotenv import load_dotenv

from database import db
from config import Config

import auth


load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():

    return """
    <h1>RunBoard</h1>

    <a href="/login">
        Login with Strava
    </a>
    """


app.add_url_rule(
    "/login",
    view_func=auth.login
)

app.add_url_rule(
    "/callback",
    view_func=auth.callback
)


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=True
    )
