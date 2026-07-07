import argparse
import os

from flask import Flask
from dotenv import load_dotenv

from database import db
from config import Config

import auth


load_dotenv()

# -------------------------------------------------
# Parse command line arguments
# -------------------------------------------------
parser = argparse.ArgumentParser(
    description="360 Long Runners - Strava Authorization Server"
)

parser.add_argument(
    "--app",
    metavar="APP_NAME",
    help="Temporarily override the Strava application used for authorization.",
)

args = parser.parse_args()

# Make the selected app available to the application
if args.app:
    os.environ["AUTHORIZATION_APP_OVERRIDE"] = args.app

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():

    override = os.getenv("AUTHORIZATION_APP_OVERRIDE")

    if override:
        auth_app = f"{override} (Command Line Override)"
    else:
        auth_app = "Default (settings/strava_apps.yml)"

    return f"""
    <h1>🏃 360 Long Runners</h1>

    <p><b>Authorization App:</b> {auth_app}</p>

    <br>

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

    override = os.getenv("AUTHORIZATION_APP_OVERRIDE")

    print("=" * 60)
    print("360 Long Runners - Authorization Server")

    if override:
        print(f"Authorization App : {override} (Command Line Override)")
    else:
        print("Authorization App : Default (settings/strava_apps.yml)")

    print("Open: http://127.0.0.1:8080")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=True
    )